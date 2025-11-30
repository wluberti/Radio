"""
Now Playing panel - shows current station and playback controls.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Pango
from typing import Optional, Dict


class NowPlayingPanel(Gtk.Box):
    """Panel displaying currently playing station and controls."""

    def __init__(self, on_play_clicked, on_stop_clicked, on_favorite_toggled, on_volume_changed):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        self.callbacks = {
            'play': on_play_clicked,
            'stop': on_stop_clicked,
            'favorite': on_favorite_toggled,
            'volume': on_volume_changed,
        }

        self.current_station: Optional[Dict] = None
        self.is_playing = False
        self.is_favorite = False

        self._build_ui()

    def _build_ui(self):
        """Build the UI components."""
        # Station name label (large, bold)
        self.station_label = Gtk.Label()
        self.station_label.set_markup('<span size="x-large" weight="bold">No Station Selected</span>')
        self.station_label.set_wrap(True)
        self.station_label.set_max_width_chars(50)
        self.station_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.append(self.station_label)

        # Current track/title label
        self.title_label = Gtk.Label()
        self.title_label.set_markup('<span size="medium">—</span>')
        self.title_label.set_wrap(True)
        self.title_label.set_max_width_chars(50)
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.append(self.title_label)

        # Bitrate and codec info
        self.info_label = Gtk.Label()
        self.info_label.set_markup('<span size="small" foreground="#888888">—</span>')
        self.append(self.info_label)

        # Playback controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        controls_box.set_halign(Gtk.Align.CENTER)
        controls_box.set_margin_top(12)

        # Play button
        self.play_button = Gtk.Button(label="▶ Play")
        self.play_button.add_css_class("suggested-action")
        self.play_button.set_size_request(100, -1)
        self.play_button.connect('clicked', self._on_play_clicked)
        controls_box.append(self.play_button)

        # Stop button
        self.stop_button = Gtk.Button(label="⏹ Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.set_size_request(100, -1)
        self.stop_button.set_sensitive(False)
        self.stop_button.connect('clicked', self._on_stop_clicked)
        controls_box.append(self.stop_button)

        # Favorite button
        self.fav_button = Gtk.ToggleButton(label="☆ Favorite")
        self.fav_button.set_size_request(100, -1)
        self.fav_button.set_sensitive(False)
        self.fav_button.connect('toggled', self._on_favorite_toggled)
        controls_box.append(self.fav_button)

        self.append(controls_box)

        # Volume control
        volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        volume_box.set_halign(Gtk.Align.CENTER)
        volume_box.set_margin_top(12)

        volume_label = Gtk.Label(label="🔊 Volume:")
        volume_box.append(volume_label)

        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_scale.set_value(80)
        self.volume_scale.set_size_request(200, -1)
        self.volume_scale.set_draw_value(True)
        self.volume_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.volume_scale.connect('value-changed', self._on_volume_changed)
        volume_box.append(self.volume_scale)

        self.append(volume_box)

    def set_station(self, station: Dict, is_favorite: bool = False):
        """Set the current station."""
        self.current_station = station
        self.is_favorite = is_favorite

        # Update station name
        name = GLib.markup_escape_text(station.get('name', 'Unknown Station'))
        country = station.get('country', '')
        if country:
            country = GLib.markup_escape_text(country)
            self.station_label.set_markup(
                f'<span size="x-large" weight="bold">{name}</span>\n'
                f'<span size="small" foreground="#888888">{country}</span>'
            )
        else:
            self.station_label.set_markup(f'<span size="x-large" weight="bold">{name}</span>')

        # Update info
        codec = station.get('codec', '').upper()
        bitrate = station.get('bitrate', 0)
        if codec or bitrate:
            info_parts = []
            if codec:
                info_parts.append(codec)
            if bitrate:
                info_parts.append(f"{bitrate} kbps")
            info = " • ".join(info_parts)
            self.info_label.set_markup(f'<span size="small" foreground="#888888">{info}</span>')

        # Update favorite button
        self.fav_button.set_sensitive(True)
        self.fav_button.set_active(is_favorite)
        self._update_favorite_button_label()

        # Enable play button
        self.play_button.set_sensitive(True)

    def set_playing(self, playing: bool):
        """Update UI for playing state."""
        self.is_playing = playing
        self.play_button.set_sensitive(not playing)
        self.stop_button.set_sensitive(playing)

    def update_title(self, title: str):
        """Update the now playing title."""
        if title:
            escaped = GLib.markup_escape_text(title)
            self.title_label.set_markup(f'<span size="medium">♫ {escaped}</span>')
        else:
            self.title_label.set_markup('<span size="medium">—</span>')

    def update_bitrate(self, bitrate: str):
        """Update the bitrate display."""
        if self.current_station:
            codec = self.current_station.get('codec', '').upper()
            info_parts = []
            if codec:
                info_parts.append(codec)
            if bitrate:
                info_parts.append(f"{bitrate} kbps")
            if info_parts:
                info = " • ".join(info_parts)
                self.info_label.set_markup(f'<span size="small" foreground="#888888">{info}</span>')

    def update_favorite_status(self, is_favorite: bool):
        """Update favorite status (external change)."""
        self.is_favorite = is_favorite
        self.fav_button.set_active(is_favorite)
        self._update_favorite_button_label()

    def _update_favorite_button_label(self):
        """Update favorite button label based on state."""
        if self.fav_button.get_active():
            self.fav_button.set_label("★ Favorite")
        else:
            self.fav_button.set_label("☆ Favorite")

    def _on_play_clicked(self, button):
        """Handle play button click."""
        if self.current_station and self.callbacks['play']:
            self.callbacks['play'](self.current_station)

    def _on_stop_clicked(self, button):
        """Handle stop button click."""
        if self.callbacks['stop']:
            self.callbacks['stop']()

    def _on_favorite_toggled(self, button):
        """Handle favorite button toggle."""
        if self.current_station and self.callbacks['favorite']:
            is_fav = button.get_active()
            self.callbacks['favorite'](self.current_station, is_fav)
            self._update_favorite_button_label()

    def _on_volume_changed(self, scale):
        """Handle volume slider change."""
        if self.callbacks['volume']:
            volume = scale.get_value() / 100.0
            self.callbacks['volume'](volume)

    def set_volume(self, volume: float):
        """Set volume slider position (0.0 to 1.0)."""
        self.volume_scale.set_value(volume * 100)

    def reset(self):
        """Reset to initial state."""
        self.current_station = None
        self.is_playing = False
        self.is_favorite = False

        self.station_label.set_markup('<span size="x-large" weight="bold">No Station Selected</span>')
        self.title_label.set_markup('<span size="medium">—</span>')
        self.info_label.set_markup('<span size="small" foreground="#888888">—</span>')

        self.play_button.set_sensitive(False)
        self.stop_button.set_sensitive(False)
        self.fav_button.set_sensitive(False)
        self.fav_button.set_active(False)
        self._update_favorite_button_label()
