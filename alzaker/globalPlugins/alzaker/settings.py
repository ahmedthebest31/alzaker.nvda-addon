import webbrowser as web
from typing import Any
import wx

from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
import ui
import config

class AlzakerSettingsPanel(SettingsPanel):
    title = "الذاكر"
    main_plugin: Any = None

    def makeSettings(self, settingsSizer: wx.Sizer) -> None:
        if self.main_plugin is None:
            raise ValueError("البلجن الأساسي غير متصل بالواجهة")

        cfg = self.main_plugin.cfg
        sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

        # زر التفعيل والإيقاف
        self.chk_enable = sHelper.addItem(wx.CheckBox(self, label="تفعيل إضافة الذاكر التلقائي"))
        self.chk_enable.SetValue(cfg["enabled"])

        # نوع التذكير
        sHelper.addItem(wx.StaticText(self, label="نوع التذكير:", name="type_lbl"))
        self.choice_type = sHelper.addItem(wx.Choice(self, name="type_lbl"))
        self.choice_type.Set(["النطق الصوتي (TTS)", "ملفات صوتية", "إشعار ويندوز (Notification)"])
        self.choice_type.SetSelection(cfg["type"])

        # المدة بالدقائق (المينيمم 1 عشان مفيش حاجة اسمها 0 وتعمل لوب لا نهائي يهنج الجهاز)
        sHelper.addItem(wx.StaticText(self, label="المدة بين كل تذكير (بالدقائق):", name="interval_lbl"))
        self.spin_interval = sHelper.addItem(wx.SpinCtrl(self, name="interval_lbl", min=1, max=500))
        self.spin_interval.SetValue(cfg["interval"] if cfg["interval"] > 0 else 1)

        # شريط مستوى الصوت للملفات الصوتية
        sHelper.addItem(wx.StaticText(self, label="مستوى الصوت للملفات الصوتية:", name="vol_lbl"))
        self.slider_volume = sHelper.addItem(wx.Slider(self, name="vol_lbl", value=cfg["volume"], minValue=0, maxValue=100, style=wx.SL_HORIZONTAL))

        # زر التبرع
        btn_donate = sHelper.addItem(wx.Button(self, label="تبرع للمطور"))
        btn_donate.Bind(wx.EVT_BUTTON, self.on_donate)

    def postInit(self) -> None:
        self.chk_enable.SetFocus()

    def onSave(self) -> None:
        if self.main_plugin is None:
            return

        cfg = self.main_plugin.cfg
        
        # تحديث الإعدادات
        cfg["enabled"] = self.chk_enable.GetValue()
        cfg["type"] = self.choice_type.GetSelection()
        cfg["interval"] = self.spin_interval.GetValue()
        cfg["volume"] = self.slider_volume.GetValue()
        config.conf.save()

        # إعادة تشغيل الثريد بالمعطيات الجديدة فوراً بدون إعادة تشغيل NVDA
        self.main_plugin.restart_thread()

    def on_donate(self, event: wx.Event) -> None:
        ui.message("يرجى الانتظار...")
        web.open("https://www.paypal.me/ahmedthebest31")