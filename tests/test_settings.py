from types import SimpleNamespace

from tests.conftest import load_plugin_module


def test_cfg_property_returns_config_section(monkeypatch):
	plugin_module = load_plugin_module(monkeypatch)

	plugin = SimpleNamespace()
	plugin_module.GlobalPlugin.cfg.fget(plugin)

	from tests.conftest import FakeConfig

	cfg = FakeConfig()
	assert cfg["alzaker"] == {}
