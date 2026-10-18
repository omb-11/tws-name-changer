"""Small settings store; it deliberately never stores Bluetooth credentials."""
import json
from pathlib import Path

class Settings:
    def __init__(self, path: Path) -> None: self.path = path
    def load(self) -> dict[str, str]:
        try: data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError): return {}
        return {str(key): str(value) for key, value in data.items()}
    def save(self, values: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(values, indent=2), encoding="utf-8")
