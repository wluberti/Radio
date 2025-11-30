"""
Main application window for PyRadio.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from typing import Dict, Optional

from .now_playing import NowPlayingPanel
from .station_list import StationListView
from ..player import Player
from ..favorites import FavoritesManager
from ..station_fetcher import StationFetcher
from ..config import Config


class MainWindow(Gtk.ApplicationWindow):
    """Main application window."""

    def __init__(self, app, config: Config):
        super().__init__(application=app, title="PyRadio")

        self.config = config

        # Initialize components
        self.player = Player()
        self.favorites = FavoritesManager(config)
        self.fetcher = StationFetcher()

        # Connect player signals
        self.player.connect('metadata-changed', self._on_metadata_changed)
        self.player.connect('state-changed', self._on_state_changed)
        self.player.connect('error', self._on_player_error)

        # State
        self.all_stations = []
        self.current_view = "all"  # "all" or "favorites"
        self.current_station: Optional[Dict] = None

        # Build UI
        self.set_default_size(900, 600)
        self._build_ui()

        # Load stations
        GLib.idle_add(self._load_stations)

        # Set initial volume
        saved_volume = self.config.get_setting('volume', 0.8)
        self.player.set_volume(saved_volume)
        self.now_playing.set_volume(saved_volume)

    def _build_ui(self):
        """Build the main window UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)

        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search stations...")
        self.search_entry.set_size_request(300, -1)
        self.search_entry.connect('search-changed', self._on_search_changed)
        header.set_title_widget(self.search_entry)

        self.set_titlebar(header)

        # View switcher (All Stations / Favorites)
        switcher_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        switcher_box.add_css_class("linked")
        switcher_box.set_halign(Gtk.Align.CENTER)
        switcher_box.set_margin_top(8)
        switcher_box.set_margin_bottom(8)

        self.all_button = Gtk.ToggleButton(label="All Stations")
        self.all_button.set_active(True)
        self.all_button.connect('toggled', self._on_view_toggled, "all")
        switcher_box.append(self.all_button)

        self.fav_button = Gtk.ToggleButton(label="Favorites")
        self.fav_button.connect('toggled', self._on_view_toggled, "favorites")
        switcher_box.append(self.fav_button)

        main_box.append(switcher_box)

        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(separator)

        # Paned container (station list + now playing)
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_vexpand(True)
        paned.set_position(500)

        # Station list
        self.station_list = StationListView(
            on_station_selected=self._on_station_selected,
            on_station_activated=self._on_station_activated,
            is_favorite_func=lambda uuid: self.favorites.is_favorite(uuid)
        )
        paned.set_start_child(self.station_list)

        # Now playing panel
        self.now_playing = NowPlayingPanel(
            on_play_clicked=self._on_play_clicked,
            on_stop_clicked=self._on_stop_clicked,
            on_favorite_toggled=self._on_favorite_toggled,
            on_volume_changed=self._on_volume_changed
        )
        paned.set_end_child(self.now_playing)

        main_box.append(paned)

        # Status bar
        self.status_bar = Gtk.Label()
        self.status_bar.set_markup('<span size="small">Ready</span>')
        self.status_bar.set_margin_start(8)
        self.status_bar.set_margin_end(8)
        self.status_bar.set_margin_top(4)
        self.status_bar.set_margin_bottom(4)
        self.status_bar.set_xalign(0)
        main_box.append(self.status_bar)

        self.set_child(main_box)

    def _load_stations(self):
        """Load stations from cache or API."""
        # Try to load from cache first
        if self.config.is_cache_valid():
            self.all_stations = self.config.load_cache()
            if self.all_stations:
                self._update_status(f"Loaded {len(self.all_stations)} stations from cache")
                self._update_station_list()
                return

        # Fetch from API
        self._update_status("Fetching stations from RadioBrowser...")

        try:
            # Fetch mixed stations (Dutch + international)
            self.all_stations = self.fetcher.fetch_mixed_stations()

            if self.all_stations:
                # Save to cache
                self.config.save_cache(self.all_stations)
                self._update_status(f"Loaded {len(self.all_stations)} stations")
                self._update_station_list()
            else:
                self._update_status("Failed to fetch stations - check network connection")
        except Exception as e:
            self._update_status(f"Error fetching stations: {e}")
            print(f"Station fetch error: {e}")

    def _update_station_list(self):
        """Update the station list based on current view."""
        if self.current_view == "all":
            self.station_list.set_stations(self.all_stations)
        else:  # favorites
            self.station_list.set_stations(self.favorites.get_all())

        # Select first station if none selected
        if not self.current_station:
            self.station_list.select_first()

    def _update_status(self, message: str):
        """Update status bar message."""
        escaped = GLib.markup_escape_text(message)
        self.status_bar.set_markup(f'<span size="small">{escaped}</span>')

    def _on_search_changed(self, entry):
        """Handle search text change."""
        search_text = entry.get_text()
        self.station_list.set_filter(search_text)

    def _on_view_toggled(self, button, view_name):
        """Handle view switcher toggle."""
        if not button.get_active():
            return

        self.current_view = view_name

        # Update other button
        if view_name == "all":
            self.fav_button.set_active(False)
        else:
            self.all_button.set_active(False)

        # Clear search
        self.search_entry.set_text("")

        # Update list
        self._update_station_list()

    def _on_station_selected(self, station: Dict):
        """Handle station selection."""
        self.current_station = station
        is_fav = self.favorites.is_favorite(station.get('stationuuid', ''))
        self.now_playing.set_station(station, is_fav)

    def _on_station_activated(self, station: Dict):
        """Handle station activation (double-click)."""
        self.current_station = station
        is_fav = self.favorites.is_favorite(station.get('stationuuid', ''))
        self.now_playing.set_station(station, is_fav)
        self._on_play_clicked(station)

    def _on_play_clicked(self, station: Dict):
        """Handle play button click."""
        url = station.get('url')
        if url:
            self._update_status(f"Playing: {station.get('name', 'Unknown')}")
            self.player.play(url)
            self.now_playing.set_playing(True)

    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.player.stop()
        self.now_playing.set_playing(False)
        self._update_status("Stopped")

    def _on_favorite_toggled(self, station: Dict, is_favorite: bool):
        """Handle favorite toggle."""
        if is_favorite:
            self.favorites.add(station)
            self._update_status(f"Added to favorites: {station.get('name', 'Unknown')}")
        else:
            self.favorites.remove(station.get('stationuuid', ''))
            self._update_status(f"Removed from favorites: {station.get('name', 'Unknown')}")

        # Refresh station list to update favorite indicators
        self.station_list.refresh()

        # If in favorites view, update list
        if self.current_view == "favorites":
            self._update_station_list()

    def _on_volume_changed(self, volume: float):
        """Handle volume change."""
        self.player.set_volume(volume)
        self.config.set_setting('volume', volume)

    def _on_metadata_changed(self, player, key: str, value: str):
        """Handle metadata updates from player."""
        if key == 'title':
            self.now_playing.update_title(value)
            if self.current_station:
                name = self.current_station.get('name', 'Unknown')
                self._update_status(f"♫ {name}: {value}")
        elif key == 'bitrate':
            self.now_playing.update_bitrate(value)

    def _on_state_changed(self, player, state: str):
        """Handle player state changes."""
        # Could update UI based on state if needed
        pass

    def _on_player_error(self, player, error: str):
        """Handle player errors."""
        self._update_status(f"Error: {error}")
        self.now_playing.set_playing(False)

        # Show error dialog
        dialog = Gtk.AlertDialog()
        dialog.set_message("Playback Error")
        dialog.set_detail(error)
        dialog.set_buttons(["OK"])
        dialog.choose(self, None, None)

    def cleanup(self):
        """Clean up resources before closing."""
        self.player.cleanup()
