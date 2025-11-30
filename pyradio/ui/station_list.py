"""
Station list view - displays radio stations in a scrollable list.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Pango, GObject, Gio
from typing import List, Dict, Callable, Optional


class StationListView(Gtk.Box):
    """Scrollable list view for radio stations."""

    def __init__(self, on_station_selected, on_station_activated, is_favorite_func):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.on_station_selected = on_station_selected
        self.on_station_activated = on_station_activated
        self.is_favorite_func = is_favorite_func

        self.stations: List[Dict] = []
        self.filtered_stations: List[Dict] = []
        self.filter_text = ""

        self._build_ui()

    def _build_ui(self):
        """Build the list view UI."""
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Create list box
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect('row-selected', self._on_row_selected)
        self.list_box.connect('row-activated', self._on_row_activated)

        # Add some styling
        self.list_box.add_css_class("navigation-sidebar")

        scrolled.set_child(self.list_box)
        self.append(scrolled)

        # Status label for empty state
        self.status_label = Gtk.Label()
        self.status_label.set_markup('<span size="large" foreground="#888888">Loading stations...</span>')
        self.status_label.set_margin_top(40)
        self.status_label.set_margin_bottom(40)

    def set_stations(self, stations: List[Dict]):
        """Set the list of stations to display."""
        self.stations = stations
        self._apply_filter()

    def set_filter(self, filter_text: str):
        """Filter stations by search text."""
        self.filter_text = filter_text.lower()
        self._apply_filter()

    def _apply_filter(self):
        """Apply current filter and rebuild list."""
        # Filter stations
        if not self.filter_text:
            self.filtered_stations = self.stations
        else:
            self.filtered_stations = [
                s for s in self.stations
                if self.filter_text in s.get('name', '').lower() or
                   self.filter_text in s.get('country', '').lower() or
                   self.filter_text in s.get('tags', '').lower()
            ]

        # Rebuild list
        self._rebuild_list()

    def _rebuild_list(self):
        """Rebuild the list box with current filtered stations, grouped by country."""
        # Clear existing rows
        while True:
            row = self.list_box.get_row_at_index(0)
            if row is None:
                break
            self.list_box.remove(row)

        # Add new rows
        if not self.filtered_stations:
            # Show empty state
            if self.filter_text:
                self.status_label.set_markup(
                    '<span size="large" foreground="#888888">No stations found</span>'
                )
            else:
                self.status_label.set_markup(
                    '<span size="large" foreground="#888888">No stations available</span>'
                )
            self.list_box.append(self.status_label)
        else:
            # Group stations by country
            from collections import defaultdict
            countries = defaultdict(list)
            for station in self.filtered_stations:
                country = station.get('country', 'Unknown')
                countries[country].append(station)

            # Sort countries: Netherlands first, then alphabetically
            sorted_countries = sorted(countries.keys(),
                                     key=lambda c: (c != 'The Netherlands', c.lower()))

            # Add stations grouped by country
            for country in sorted_countries:
                # Add country header
                header_row = Gtk.ListBoxRow()
                header_row.set_selectable(False)
                header_row.set_activatable(False)
                header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                header_box.set_margin_start(12)
                header_box.set_margin_end(12)
                header_box.set_margin_top(12)
                header_box.set_margin_bottom(4)

                country_label = Gtk.Label()
                escaped_country = GLib.markup_escape_text(country)
                count = len(countries[country])
                country_label.set_markup(
                    f'<span weight="bold" size="small" foreground="#666666">'
                    f'{escaped_country.upper()} ({count})</span>'
                )
                country_label.set_xalign(0)
                header_box.append(country_label)
                header_row.set_child(header_box)
                self.list_box.append(header_row)

                # Add stations for this country
                for station in countries[country]:
                    row = self._create_station_row(station)
                    self.list_box.append(row)


    def _create_station_row(self, station: Dict) -> Gtk.ListBoxRow:
        """Create a list box row for a station."""
        row = Gtk.ListBoxRow()
        row.station_data = station  # Attach station data to row

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        # Station info box (vertical)
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info_box.set_hexpand(True)

        # Station name
        name_label = Gtk.Label()
        name = GLib.markup_escape_text(station.get('name', 'Unknown Station'))
        name_label.set_markup(f'<span weight="bold">{name}</span>')
        name_label.set_xalign(0)
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        info_box.append(name_label)

        # Station details (country, codec, bitrate)
        details = []
        country = station.get('country', '')
        if country:
            details.append(country)

        codec = station.get('codec', '').upper()
        if codec:
            details.append(codec)

        bitrate = station.get('bitrate', 0)
        if bitrate:
            details.append(f"{bitrate} kbps")

        if details:
            details_text = " • ".join(details)
            details_label = Gtk.Label()
            details_label.set_markup(f'<span size="small" foreground="#888888">{details_text}</span>')
            details_label.set_xalign(0)
            details_label.set_ellipsize(Pango.EllipsizeMode.END)
            info_box.append(details_label)

        box.append(info_box)

        # Favorite indicator
        if self.is_favorite_func and self.is_favorite_func(station.get('stationuuid', '')):
            fav_label = Gtk.Label(label="★")
            fav_label.add_css_class("accent")
            box.append(fav_label)

        row.set_child(box)
        return row

    def _on_row_selected(self, list_box, row):
        """Handle row selection."""
        if row and hasattr(row, 'station_data') and self.on_station_selected:
            self.on_station_selected(row.station_data)

    def _on_row_activated(self, list_box, row):
        """Handle row activation (double-click or Enter)."""
        if row and hasattr(row, 'station_data') and self.on_station_activated:
            self.on_station_activated(row.station_data)

    def refresh(self):
        """Refresh the list (e.g., after favorites change)."""
        self._rebuild_list()

    def select_first(self):
        """Select the first station in the list (skip headers)."""
        # Find first selectable row (skip country headers)
        index = 0
        while True:
            row = self.list_box.get_row_at_index(index)
            if row is None:
                break
            if row.get_selectable() and hasattr(row, 'station_data'):
                self.list_box.select_row(row)
                break
            index += 1
