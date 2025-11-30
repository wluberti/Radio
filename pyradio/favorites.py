"""
Favorites management for PyRadio.
Handles adding, removing, and persisting favorite stations.
"""

from typing import List, Dict, Optional
from .config import Config


class FavoritesManager:
    """Manages user's favorite radio stations."""

    def __init__(self, config: Config):
        self.config = config
        self._favorites: List[Dict] = []
        self._load()

    def _load(self):
        """Load favorites from config."""
        self._favorites = self.config.load_favorites()

    def _save(self):
        """Save favorites to config."""
        self.config.save_favorites(self._favorites)

    def add(self, station: Dict) -> bool:
        """Add a station to favorites. Returns True if added, False if already existed."""
        uuid = station.get('stationuuid')
        if not uuid:
            return False

        # Check if already in favorites
        if self.is_favorite(uuid):
            return False

        self._favorites.append(station)
        self._save()
        return True

    def remove(self, station_uuid: str) -> bool:
        """Remove a station from favorites by UUID. Returns True if removed."""
        initial_len = len(self._favorites)
        self._favorites = [s for s in self._favorites if s.get('stationuuid') != station_uuid]

        if len(self._favorites) < initial_len:
            self._save()
            return True
        return False

    def toggle(self, station: Dict) -> bool:
        """Toggle favorite status. Returns True if now favorite, False if removed."""
        uuid = station.get('stationuuid')
        if not uuid:
            return False

        if self.is_favorite(uuid):
            self.remove(uuid)
            return False
        else:
            self.add(station)
            return True

    def is_favorite(self, station_uuid: str) -> bool:
        """Check if a station is in favorites."""
        return any(s.get('stationuuid') == station_uuid for s in self._favorites)

    def get_all(self) -> List[Dict]:
        """Get all favorite stations."""
        return self._favorites.copy()

    def get_count(self) -> int:
        """Get number of favorite stations."""
        return len(self._favorites)

    def clear(self):
        """Remove all favorites."""
        self._favorites = []
        self._save()
