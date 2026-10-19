import json
from pathlib import Path
from tws_name_changer.storage.settings import Settings, default_settings_path, get_app_data_dir


def test_get_app_data_dir_contains_app_name():
    path = get_app_data_dir()
    assert isinstance(path, Path)
    assert "TWSNameChanger" in str(path)


def test_default_settings_path():
    path = default_settings_path()
    assert path.name == "settings.json"


def test_settings_load_nonexistent_returns_empty(tmp_path: Path):
    s = Settings(tmp_path / "nonexistent.json")
    assert s.load() == {}


def test_settings_load_corrupted_json(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not: valid: json", encoding="utf-8")
    s = Settings(p)
    assert s.load() == {}


def test_settings_save_and_load(tmp_path: Path):
    p = tmp_path / "subdir" / "settings.json"
    s = Settings(p)
    s.save({"theme": "dark", "timeout": "10"})
    assert p.exists()
    assert s.load() == {"theme": "dark", "timeout": "10"}


def test_settings_get_and_set(tmp_path: Path):
    p = tmp_path / "settings.json"
    s = Settings(p)
    assert s.get("missing", "default_val") == "default_val"
    s.set("key1", "value1")
    assert s.get("key1") == "value1"
