import sys
import builtins
from types import SimpleNamespace


class FakeConfig(dict):
	def __init__(self):
		super().__init__({"alzaker": {}})
		self.spec = {}

	def save(self):
		pass


def load_plugin_module(monkeypatch, tmp_path=None):
	class FakeGlobalPlugin:
		def __init__(self, *args, **kwargs):
			pass

		def terminate(self):
			pass

	def identity_script(*args, **kwargs):
		def decorator(func):
			return func

		return decorator

	monkeypatch.setattr(builtins, "_", lambda value: value, raising=False)
	monkeypatch.setitem(sys.modules, "addonHandler", SimpleNamespace(initTranslation=lambda: None))
	monkeypatch.setitem(sys.modules, "config", SimpleNamespace(conf=FakeConfig()))
	monkeypatch.setitem(sys.modules, "core", SimpleNamespace(callLater=lambda delay, func: None))
	monkeypatch.setitem(sys.modules, "api", SimpleNamespace(copyToClip=lambda text: True))
	monkeypatch.setitem(sys.modules, "ui", SimpleNamespace(message=lambda message: None))
	monkeypatch.setitem(sys.modules, "nvwave", SimpleNamespace(WavePlayer=object))
	monkeypatch.setitem(sys.modules, "inputCore", SimpleNamespace(InputGesture=object))
	monkeypatch.setitem(sys.modules, "globalPluginHandler", SimpleNamespace(GlobalPlugin=FakeGlobalPlugin))
	monkeypatch.setitem(sys.modules, "gui", SimpleNamespace(guiHelper=SimpleNamespace()))
	monkeypatch.setitem(
		sys.modules,
		"gui.settingsDialogs",
		SimpleNamespace(NVDASettingsDialog=SimpleNamespace(categoryClasses=[]), SettingsPanel=object),
	)
	monkeypatch.setitem(
		sys.modules,
		"scriptHandler",
		SimpleNamespace(script=identity_script, getLastScriptRepeatCount=lambda: 0),
	)
	monkeypatch.setitem(
		sys.modules,
		"wx",
		SimpleNamespace(
			CheckBox=object,
			Choice=object,
			StaticText=object,
			SpinCtrl=object,
			Slider=object,
			Button=object,
			Event=object,
			Sizer=object,
			SL_HORIZONTAL=0,
			EVT_BUTTON=None,
		),
	)
	monkeypatch.setitem(
		sys.modules,
		"wx.adv",
		SimpleNamespace(NotificationMessage=SimpleNamespace(Show=lambda self, timeout: None)),
	)
	monkeypatch.setitem(
		sys.modules, "logHandler", SimpleNamespace(log=SimpleNamespace(error=lambda *args, **kwargs: None))
	)
	monkeypatch.setitem(sys.modules, "threading", __import__("threading"))
	monkeypatch.setitem(sys.modules, "os", __import__("os"))
	monkeypatch.setitem(sys.modules, "wave", __import__("wave"))

	for module_name in list(sys.modules):
		if module_name.startswith("alzaker.globalPlugins.alzaker"):
			monkeypatch.delitem(sys.modules, module_name, raising=False)

	import alzaker.globalPlugins.alzaker as plugin_module

	return plugin_module
