"""
Radio station fetcher using RadioBrowser API.
Fetches stations from the public RadioBrowser directory.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Optional


class StationFetcher:
    """Fetches radio stations from RadioBrowser API."""

    # RadioBrowser API base URL (uses DNS-based load balancing)
    API_BASE = "https://de1.api.radio-browser.info/json"

    def __init__(self):
        self.user_agent = "PyRadio/1.0"

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """Make HTTP request to RadioBrowser API."""
        url = f"{self.API_BASE}/{endpoint}"

        if params:
            # Build query string
            query_parts = []
            for key, value in params.items():
                query_parts.append(f"{key}={urllib.parse.quote(str(value))}")
            if query_parts:
                url += "?" + "&".join(query_parts)

        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', self.user_agent)

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))
        except urllib.error.URLError as e:
            print(f"Network error fetching stations: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing station data: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching stations: {e}")
            return []

    def fetch_dutch_stations(self, limit: int = 500) -> List[Dict]:
        """Fetch ALL Dutch radio stations (increased limit to ensure comprehensive coverage)."""
        stations = self._make_request("stations/search", {
            "country": "The Netherlands",
            "order": "votes",
            "reverse": "true",
            "limit": limit,
            "hidebroken": "true"
        })
        return self._normalize_stations(stations)

    def fetch_top_stations(self, limit: int = 200) -> List[Dict]:
        """Fetch top-voted stations from all countries."""
        stations = self._make_request("stations/search", {
            "order": "votes",
            "reverse": "true",
            "limit": limit,
            "hidebroken": "true"
        })
        return self._normalize_stations(stations)

    def search_stations(self, query: str, limit: int = 100) -> List[Dict]:
        """Search for stations by name."""
        if not query.strip():
            return []

        stations = self._make_request("stations/search", {
            "name": query,
            "order": "votes",
            "reverse": "true",
            "limit": limit,
            "hidebroken": "true"
        })
        return self._normalize_stations(stations)

    def fetch_by_country(self, country: str, limit: int = 500) -> List[Dict]:
        """Fetch stations from a specific country."""
        stations = self._make_request("stations/search", {
            "country": country,
            "order": "votes",
            "reverse": "true",
            "limit": limit,
            "hidebroken": "true"
        })
        return self._normalize_stations(stations)

    def fetch_all_countries(self) -> List[str]:
        """Fetch list of all countries with stations."""
        try:
            countries = self._make_request("countries")
            # Sort by station count descending
            return sorted([c.get('name', '') for c in countries if c.get('name')],
                         key=lambda x: x.lower())
        except Exception:
            return []

    def fetch_mixed_stations(self) -> List[Dict]:
        """Fetch a mix of Dutch stations and international top stations."""
        # Get ALL Dutch stations first (prioritized) - increased to 500 to ensure complete coverage
        dutch = self.fetch_dutch_stations(500)

        # Get international top stations
        international = self.fetch_top_stations(150)

        # Combine, avoiding duplicates
        seen_uuids = set()
        result = []

        for station in dutch + international:
            uuid = station.get('stationuuid')
            if uuid and uuid not in seen_uuids:
                seen_uuids.add(uuid)
                result.append(station)

        return result

    def _normalize_stations(self, stations: List[Dict]) -> List[Dict]:
        """Normalize station data from API response."""
        normalized = []

        for station in stations:
            # Extract and normalize relevant fields
            normalized_station = {
                'stationuuid': station.get('stationuuid', ''),
                'name': station.get('name', 'Unknown Station'),
                'url': station.get('url_resolved') or station.get('url', ''),
                'homepage': station.get('homepage', ''),
                'favicon': station.get('favicon', ''),
                'country': station.get('country', ''),
                'countrycode': station.get('countrycode', ''),
                'language': station.get('language', ''),
                'tags': station.get('tags', ''),
                'votes': station.get('votes', 0),
                'codec': station.get('codec', ''),
                'bitrate': station.get('bitrate', 0),
            }

            # Only add stations with valid URLs
            if normalized_station['url']:
                normalized.append(normalized_station)

        return normalized
