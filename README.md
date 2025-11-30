# PyRadio - Internet Radio Player for Linux

![PyRadio Icon](data/pyradio.png)

A modern, user-friendly internet radio player for Debian-based Linux systems. Built with Python and GTK4, PyRadio provides access to thousands of radio stations from around the world, with special support for Dutch stations.

## Features

- 🌐 **Extensive Station Library**: Access to 30,000+ radio stations via RadioBrowser API
- 🇳🇱 **Dutch Radio Support**: Includes NPO Radio 1/2/3FM, Qmusic, Radio 538, Sublime, and hundreds more
- 📋 **Country-Grouped View**: Stations organized by country (Netherlands first)
- 🔄 **Refresh & Sort**: Manually refresh station list and sort by Name, Bitrate, or Popularity
- ⭐ **Favorites**: Save and organize your favorite stations
- 🎵 **Metadata Display**: Shows current song/track title and bitrate (when available)
- 🔍 **Search & Filter**: Easily find stations by name, country, or tags
- 💾 **Offline Cache**: Stations are cached locally for offline browsing
- 🎨 **Modern GTK4 Interface**: Clean, native Linux desktop experience
- 🔊 **GStreamer Backend**: Reliable playback with support for MP3, AAC, OGG formats

## Screenshots

*The application features a clean two-panel layout with station list on the left and now-playing controls on the right.*

## Requirements

### Runtime Dependencies
- Python 3.8 or higher
- GTK 4.0
- GStreamer 1.0 with plugins:
  - gstreamer1.0-plugins-base
  - gstreamer1.0-plugins-good
  - gstreamer1.0-plugins-bad
- PyGObject (python3-gi)

### Build Dependencies
- debhelper (>= 13)
- dh-python
- python3-setuptools

## Installation

### From .deb Package (Recommended)

1. Download the latest `.deb` package
2. Install it:
   ```bash
   sudo dpkg -i pyradio_1.0.0-1_all.deb
   sudo apt-get install -f  # Fix any missing dependencies
   ```
3. Launch from application menu or run `pyradio` in terminal

### From Source

1. Clone or download this repository
2. Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-gi python3-setuptools \
                        gir1.2-gtk-4.0 gir1.2-gstreamer-1.0 \
                        gstreamer1.0-plugins-base \
                        gstreamer1.0-plugins-good \
                        gstreamer1.0-plugins-bad
   ```
3. Run from source:
   ```bash
   cd /path/to/radio
   python3 -m pyradio
   ```

## Building the .deb Package

### Prerequisites

Install build tools:
```bash
sudo apt-get update
sudo apt-get install build-essential debhelper dh-python \
                     python3-all python3-setuptools python3-gi \
                     gir1.2-gtk-4.0
```

### Build Steps

1. Navigate to the project directory:
   ```bash
   cd /path/to/radio
   ```

2. Build the package:
   ```bash
   dpkg-buildpackage -us -uc -b
   ```

3. The `.deb` package will be created in the parent directory:
   ```bash
   ls ../*.deb
   ```

4. Install the package:
   ```bash
   sudo dpkg -i ../pyradio_1.0.0-1_all.deb
   sudo apt-get install -f  # Fix dependencies if needed
   ```

## Usage

### Basic Usage

1. **Launch the app**: Run `pyradio` from terminal or find "PyRadio" in your application menu
2. **Browse stations**: Scroll through the station list (Dutch stations appear first)
3. **Search**: Use the search bar in the header to filter stations by name
4. **Play a station**: Click a station to select it, then click "▶ Play"
5. **Add to favorites**: Click the "☆ Favorite" button while playing a station
6. **View favorites**: Click the "Favorites" tab at the top
7. **Adjust volume**: Use the volume slider in the now-playing panel

### Keyboard Shortcuts

- `Ctrl+Q`: Quit application
- `Ctrl+F`: Focus search box (if implemented)

### Data Storage

PyRadio stores its data in `~/.config/pyradio/`:
- `favorites.json`: Your favorite stations
- `stations_cache.json`: Cached station list
- `settings.json`: Application settings (volume, etc.)

## Troubleshooting

### No sound / Playback errors

- **Check GStreamer plugins**: Ensure all required GStreamer plugins are installed:
  ```bash
  sudo apt-get install gstreamer1.0-plugins-base \
                       gstreamer1.0-plugins-good \
                       gstreamer1.0-plugins-bad \
                       gstreamer1.0-libav
  ```

- **Test GStreamer**: Try playing a stream directly with gst-launch:
  ```bash
  gst-launch-1.0 playbin uri=http://icecast.omroep.nl/radio1-bb-mp3
  ```

### "Failed to fetch stations" error

- **Check network connection**: Ensure you have internet access
- **Firewall**: Make sure outgoing HTTPS connections are allowed
- **Cached stations**: Even offline, you can browse previously cached stations

### Application doesn't appear in menu

- **Update desktop database**:
  ```bash
  sudo update-desktop-database
  ```

### GTK4 not available (older systems)

This application requires GTK4, which is available in:
- Ubuntu 21.04+
- Debian 11 (Bullseye)+
- Linux Mint 21+

For older systems, GTK4 can be built from source or installed via flatpak.

## Architecture

PyRadio is built with a modular architecture:

- **pyradio/main.py**: GTK Application entry point
- **pyradio/config.py**: Configuration and data persistence
- **pyradio/station_fetcher.py**: RadioBrowser API client
- **pyradio/player.py**: GStreamer audio player with metadata extraction
- **pyradio/favorites.py**: Favorites management
- **pyradio/ui/**: GTK4 user interface components
  - main_window.py: Main application window
  - station_list.py: Station list view
  - now_playing.py: Playback controls and info panel

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

PyRadio is free software licensed under the GNU General Public License v3.0 or later.
See [LICENSE](LICENSE) for details.

## Credits

- **RadioBrowser API**: https://www.radio-browser.info - Free radio station directory
- **GTK**: https://www.gtk.org - Cross-platform UI toolkit
- **GStreamer**: https://gstreamer.freedesktop.org - Multimedia framework

## Changelog

### Version 1.0.0 (2025-11-30)
- Initial release
- RadioBrowser API integration
- GTK4 interface
- Favorites support
- Metadata display
- Offline caching
- Debian packaging
