
from wifisec.services import settings


def test_load_settings_returns_defaults_when_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", str(tmp_path / "settings.json"))

    assert settings.load_settings() == settings.DEFAULTS


def test_save_and_load_settings_preserve_defaults(tmp_path, monkeypatch):
    settings_path = tmp_path / "nested" / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_FILE", str(settings_path))

    settings.save_settings({"theme": "dark"})

    assert settings.load_settings() == {
        **settings.DEFAULTS,
        "theme": "dark",
    }


def test_load_settings_ignores_invalid_json(tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(settings, "SETTINGS_FILE", str(settings_path))

    assert settings.load_settings() == settings.DEFAULTS
