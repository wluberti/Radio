"""
Configuration management for PyRadio.
Handles user preferences and data persistence.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


class Config:
    """Manages application configuration and user data."""

    def __init__(self):
        # Create config directory in user's home
        self.config_dir = Path.home() / ".config" / "pyradio"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Configuration files
        self.favorites_file = self.config_dir / "favorites.json"
        self.cache_file = self.config_dir / "stations_cache.json"
        self.settings_file = self.config_dir / "settings.json"

        # Default settings
        self.settings = {
            "volume": 0.8,
            "cache_expiry_hours": 24,
            "last_station_uuid": None,
        }

        self._load_settings()

    def _load_settings(self):
        """Load user settings from disk."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}")

    def save_settings(self):
        """Save current settings to disk."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def get_setting(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set a setting value and save."""
        self.settings[key] = value
        self.save_settings()

    def load_favorites(self) -> List[Dict]:
        """Load favorite stations from disk."""
        if not self.favorites_file.exists():
            return []

        try:
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading favorites: {e}")
            return []

    def save_favorites(self, favorites: List[Dict]):
        """Save favorite stations to disk."""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving favorites: {e}")

    def load_cache(self) -> List[Dict]:
        """Load cached stations from disk."""
        if not self.cache_file.exists():
            return []

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('stations', [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading cache: {e}")
            return []

    def save_cache(self, stations: List[Dict]):
        """Save station cache to disk."""
        try:
            import time
            data = {
                'timestamp': time.time(),
                'stations': stations
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving cache: {e}")

    def is_cache_valid(self) -> bool:
        """Check if cache is still valid based on expiry time."""
        if not self.cache_file.exists():
            return False

        try:
            import time
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cache_time = data.get('timestamp', 0)
                expiry_seconds = self.settings['cache_expiry_hours'] * 3600
                return (time.time() - cache_time) < expiry_seconds
        except (json.JSONDecodeError, IOError):
            return False
