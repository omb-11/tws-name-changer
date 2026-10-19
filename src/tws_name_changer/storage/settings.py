import json
import os
from pathlib import Path


def get_app_data_dir() -> Path:
    """Return an appropriate user-level writable application data directory on Windows."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base = Path(local_app_data)
    else:
        base = Path.home() / "AppData" / "Local"
    app_dir = base / "TWSNameChanger"
    return app_dir


def default_settings_path() -> Path:
    """Default path for JSON settings file."""
    return get_app_data_dir() / "settings.json"


class Settings:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_settings_path()

    def load(self) -> dict[str, str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}
        return {str(key): str(value) for key, value in data.items()}

    def save(self, values: dict[str, str]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(values, indent=2), encoding="utf-8")
        except OSError:
            pass

    def get(self, key: str, default: str = "") -> str:
        return self.load().get(key, default)

    def set(self, key: str, value: str) -> None:
        current = self.load()
        current[key] = value
        self.save(current)

