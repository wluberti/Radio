# PyRadio - Quick Start Guide

## Fastest Way to Try It

```bash
# Navigate to project
cd {$HOME}/radio

# Run from source (no installation needed)
python3 -m pyradio
```

That's it! The app will:
1. Fetch radio stations from the internet
2. Show them in a nice GTK window
3. Let you play, favorite, and search stations

## If You Get Errors

### Missing GTK4 or GStreamer

```bash
sudo apt-get update
sudo apt-get install python3-gi gir1.2-gtk-4.0 gir1.2-gstreamer-1.0 \
                     gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                     gstreamer1.0-plugins-bad
```

### If Your System Doesn't Have GTK4

GTK4 is available on:
- Ubuntu 21.04 or newer
- Debian 11 (Bullseye) or newer
- Linux Mint 21 or newer

For older systems, you'd need to build GTK4 from source (not recommended).

## Building the .deb Package

```bash
cd {$HOME}/radio

# Use the build script (it handles dependencies)
./build-deb.sh

# Or manually
sudo apt-get install build-essential debhelper dh-python python3-all python3-setuptools
dpkg-buildpackage -us -uc -b

# Install the package
sudo dpkg -i ../pyradio_*.deb
sudo apt-get install -f

# Run installed app
pyradio
```

## Using the App

1. **Browse by Country**: Stations are grouped by country - Netherlands appears first!
2. **Refresh**: Click the refresh icon (🔄) to reload stations
3. **Sort**: Click the sort icon to order by Name, Bitrate, or Popularity
4. **Search**: Type in the search box to filter stations
5. **Play**: Click a station, then click "▶ Play"
6. **Favorite**: Click "☆ Favorite" to save stations
7. **View Favorites**: Click "Favorites" tab at top
8. **Volume**: Use the slider at bottom
9. **Stop**: Click "⏹ Stop"

## Finding Dutch Stations

The app fetches **500+ Dutch stations** including:
- All NPO stations (Radio 1, 2, 3FM, Radio 4, etc.)
- Qmusic
- Radio 538
- Sublime (multiple streams)
- 100% NL
- Sky Radio
- And hundreds more!

Dutch stations appear first in the "THE NETHERLANDS" section. Just search for:
- "NPO" - All NPO stations
- "Qmusic"
- "538" - Radio 538
- "Sublime"
- Or scroll through the Netherlands section!

Enjoy your radio! 📻
