import os
import wave
import threading
from random import choice
from typing import Any, Optional

import core
import api
import ui
import config
import nvwave
import inputCore
import globalPluginHandler
from scriptHandler import script
from wx.adv import NotificationMessage
import addonHandler

from .settings import AlzakerSettingsPanel

addonHandler.initTranslation()

ROLE_SECTION = "alzaker"
confspec = {
    "enabled": "boolean(default=true)",
    "type": "integer(default=0)",
    "interval": "integer(default=1)",
    "volume": "integer(default=50)"
}

if config.conf is not None:
    config.conf.spec[ROLE_SECTION] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "الذاكر"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        
        AlzakerSettingsPanel.main_plugin = self
        from gui.settingsDialogs import NVDASettingsDialog
        if AlzakerSettingsPanel not in NVDASettingsDialog.categoryClasses:
            NVDASettingsDialog.categoryClasses.append(AlzakerSettingsPanel)

        self.last_zkr: Optional[str] = None
        self.active_player: Optional[nvwave.WavePlayer] = None
        
        self.resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
        self.texts_cache: list[str] = []
        self.audio_cache: list[str] = []
        self._load_cache()

        self.worker_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        self.restart_thread()

    def _load_cache(self) -> None:
        text_file = os.path.join(self.resources_path, "azkar.txt")
        if os.path.exists(text_file):
            try:
                with open(text_file, "r", encoding="utf-8") as file:
                    self.texts_cache = [line.strip() for line in file.readlines() if line.strip()]
            except OSError:
                pass

        sounds_path = os.path.join(self.resources_path, "sounds")
        if os.path.exists(sounds_path):
            try:
                self.audio_cache = [
                    os.path.join(sounds_path, f) 
                    for f in os.listdir(sounds_path) 
                    if f.lower().endswith(".wav")
                ]
            except OSError:
                pass

    @property
    def cfg(self) -> dict[str, Any]:
        return config.conf[ROLE_SECTION]

    def restart_thread(self) -> None:
        self.stop_event.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
            
        if self.cfg["enabled"] and self.cfg["interval"] > 0:
            self.stop_event.clear()
            self.worker_thread = threading.Thread(target=self._reminder_worker, daemon=True)
            self.worker_thread.start()

    def _reminder_worker(self) -> None:
        while not self.stop_event.is_set():
            wait_time = self.cfg["interval"] * 60
            if self.stop_event.wait(wait_time):
                break
                
            if not self.cfg["enabled"]:
                break
                
            core.callLater(10, self.trigger_reminder)

    def trigger_reminder(self) -> None:
        if not self.texts_cache and self.cfg["type"] != 1:
            return
            
        rem_type = self.cfg["type"]
        
        if rem_type == 0:
            self.last_zkr = choice(self.texts_cache)
            ui.message(self.last_zkr)
            
        elif rem_type == 1:
            if self.audio_cache:
                audio_file = choice(self.audio_cache)
                self._play_independent_audio(audio_file)
                
        elif rem_type == 2:
            self.last_zkr = choice(self.texts_cache)
            NotificationMessage("الذاكر", self.last_zkr).Show(50)

    def _play_independent_audio(self, filepath: str) -> None:
        try:
            with wave.open(str(filepath), "rb") as wf:
                player = nvwave.WavePlayer(
                    channels=wf.getnchannels(),
                    samplesPerSec=wf.getframerate(),
                    bitsPerSample=wf.getsampwidth() * 8
                )
                player.setVolume(all=self.cfg["volume"] / 100)
                data = wf.readframes(wf.getnframes())
                self.active_player = player

            # الحل الهندسي: تشغيل بيانات الصوت في Thread فرعي لمنع الشلل
            def feed_worker() -> None:
                try:
                    player.feed(data)
                except Exception:
                    pass

            threading.Thread(target=feed_worker, daemon=True).start()
        except Exception:
            pass

    @script(gesture="kb:NVDA+alt+z")
    def script_force_reminder(self, gesture: inputCore.InputGesture) -> None:
        if self.texts_cache:
            self.last_zkr = choice(self.texts_cache)
            ui.message(self.last_zkr)
        else:
            ui.message("ملف الأذكار غير موجود أو فارغ")
    script_force_reminder.__doc__ = "نطق ذكر عشوائي فوراً"

    @script(gesture="kb:NVDA+alt+x")
    def script_copy_last(self, gesture: inputCore.InputGesture) -> None:
        if self.last_zkr:
            if api.copyToClip(self.last_zkr):
                ui.message("تم نسخ الذكر الأخير إلى الحافظة")
        else:
            ui.message("لم يتم نطق أي ذكر لنسخه بعد")
    script_copy_last.__doc__ = "نسخ الذكر الأخير إلى الحافظة"

    def terminate(self) -> None:
        self.stop_event.set()
        if self.active_player:
            self.active_player.stop()
            
        from gui.settingsDialogs import NVDASettingsDialog
        try:
            NVDASettingsDialog.categoryClasses.remove(AlzakerSettingsPanel)
        except ValueError:
            pass
            
        super().terminate()