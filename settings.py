"""Persistent settings management."""
import json
import os
from typing import Any, Dict

SETTINGS_FILE = os.path.expanduser('~/.config/conway/settings.json')

# Default settings
DEFAULTS = {
    'theme': 'classic',
    'show_grid_lines': False,
    'wrap_mode': 'toroidal',
}


class Settings:
    """Manages persistent application settings."""

    def __init__(self):
        self._settings: Dict[str, Any] = DEFAULTS.copy()
        self.load()

    def load(self):
        """Load settings from file."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    saved = json.load(f)
                    self._settings.update(saved)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults on error

    def save(self):
        """Save settings to file."""
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self._settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value and save."""
        self._settings[key] = value
        self.save()


# Global settings instance
settings = Settings()
