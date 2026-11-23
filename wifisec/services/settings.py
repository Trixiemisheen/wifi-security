"""JSON settings persistence."""
import json
import os

from wifisec.core.config import SETTINGS_FILE

DEFAULTS = {
    "theme": "dev_cyan",
    "density": "comfortable",
    "default_interface": "",
    "wordlist_path": "",
    "update_on_startup": True,
}


def load_settings() -> dict:
    settings = dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings.update(json.load(f))
    except (OSError, json.JSONDecodeError):
        pass
    return settings


def save_settings(settings: dict) -> None:
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    merged = {**DEFAULTS, **settings}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)