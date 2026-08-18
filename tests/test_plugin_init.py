from types import SimpleNamespace

from tests.conftest import load_plugin_module


def test_load_cache_reads_azkar_text_file(monkeypatch, tmp_path):
	azkar_file = tmp_path / "azkar.txt"
	azkar_file.write_text("سبحان الله\nالحمد لله\nالله أكبر\n", encoding="utf-8")

	plugin_module = load_plugin_module(monkeypatch)

	plugin = SimpleNamespace(
		resources_path=str(tmp_path),
		texts_cache=[],
		audio_cache=[],
	)
	plugin_module.GlobalPlugin._load_cache(plugin)

	assert len(plugin.texts_cache) == 3
	assert "سبحان الله" in plugin.texts_cache


def test_load_cache_handles_missing_text_file(monkeypatch, tmp_path):
	plugin_module = load_plugin_module(monkeypatch)

	plugin = SimpleNamespace(
		resources_path=str(tmp_path),
		texts_cache=[],
		audio_cache=[],
	)
	plugin_module.GlobalPlugin._load_cache(plugin)

	assert plugin.texts_cache == []


def test_load_cache_reads_audio_files(monkeypatch, tmp_path):
	sounds_dir = tmp_path / "sounds"
	sounds_dir.mkdir()
	(sounds_dir / "azkar1.wav").write_bytes(b"fake")
	(sounds_dir / "azkar2.wav").write_bytes(b"fake")
	(sounds_dir / "readme.txt").write_text("not a sound")

	plugin_module = load_plugin_module(monkeypatch)

	plugin = SimpleNamespace(
		resources_path=str(tmp_path),
		texts_cache=[],
		audio_cache=[],
	)
	plugin_module.GlobalPlugin._load_cache(plugin)

	assert len(plugin.audio_cache) == 2
	assert all(f.endswith(".wav") for f in plugin.audio_cache)


def test_trigger_reminder_speaks_when_type_is_zero(monkeypatch, tmp_path):
	plugin_module = load_plugin_module(monkeypatch)

	spoken = []
	monkeypatch.setattr(
		__import__("ui"),
		"message",
		lambda msg: spoken.append(msg),
		raising=False,
	)

	plugin = SimpleNamespace(
		texts_cache=["سبحان الله", "الحمد لله"],
		audio_cache=[],
		cfg={"type": 0, "enabled": True, "interval": 1, "volume": 50},
		last_zkr=None,
	)
	plugin_module.GlobalPlugin.trigger_reminder(plugin)

	assert len(spoken) == 1
	assert spoken[0] in ["سبحان الله", "الحمد لله"]
	assert plugin.last_zkr == spoken[0]


def test_trigger_reminder_does_nothing_when_no_texts(monkeypatch, tmp_path):
	plugin_module = load_plugin_module(monkeypatch)

	spoken = []
	monkeypatch.setattr(
		__import__("ui"),
		"message",
		lambda msg: spoken.append(msg),
		raising=False,
	)

	plugin = SimpleNamespace(
		texts_cache=[],
		audio_cache=[],
		cfg={"type": 0, "enabled": True, "interval": 1, "volume": 50},
		last_zkr=None,
	)
	plugin_module.GlobalPlugin.trigger_reminder(plugin)

	assert spoken == []
