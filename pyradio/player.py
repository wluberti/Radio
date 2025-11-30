"""
Audio player using GStreamer for internet radio streaming.
Handles playback and metadata extraction.
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
from typing import Optional, Callable


class Player(GObject.GObject):
    """GStreamer-based audio player for internet radio streams."""

    # Custom signals for UI updates
    __gsignals__ = {
        'metadata-changed': (GObject.SignalFlags.RUN_FIRST, None, (str, str)),  # (key, value)
        'state-changed': (GObject.SignalFlags.RUN_FIRST, None, (str,)),  # state name
        'error': (GObject.SignalFlags.RUN_FIRST, None, (str,)),  # error message
    }

    def __init__(self):
        super().__init__()

        # Initialize GStreamer
        Gst.init(None)

        # Create playbin element (handles everything)
        self.playbin = Gst.ElementFactory.make('playbin', 'player')
        if not self.playbin:
            raise RuntimeError("Failed to create GStreamer playbin")

        # Connect to bus for messages
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_message)

        # Current stream info
        self.current_url: Optional[str] = None
        self.current_title: Optional[str] = None
        self.current_bitrate: Optional[int] = None
        self.is_playing: bool = False

    def play(self, url: str):
        """Start playing a radio stream."""
        if not url:
            return

        # Stop current playback
        self.stop()

        # Set new URI
        self.current_url = url
        self.playbin.set_property('uri', url)

        # Start playback
        ret = self.playbin.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            self.emit('error', f"Failed to start playback of {url}")
            return

        self.is_playing = True
        self.emit('state-changed', 'playing')

    def stop(self):
        """Stop playback."""
        self.playbin.set_state(Gst.State.NULL)
        self.is_playing = False
        self.current_url = None
        self.current_title = None
        self.current_bitrate = None
        self.emit('state-changed', 'stopped')

    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)."""
        self.playbin.set_property('volume', max(0.0, min(1.0, volume)))

    def get_volume(self) -> float:
        """Get current volume (0.0 to 1.0)."""
        return self.playbin.get_property('volume')

    def _on_message(self, bus, message):
        """Handle GStreamer bus messages."""
        t = message.type

        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            error_msg = f"Playback error: {err.message}"
            print(error_msg)
            if debug:
                print(f"Debug info: {debug}")
            self.emit('error', error_msg)
            self.stop()

        elif t == Gst.MessageType.EOS:
            # End of stream (shouldn't happen for radio, but handle anyway)
            self.stop()

        elif t == Gst.MessageType.TAG:
            # Metadata tags (song title, bitrate, etc.)
            taglist = message.parse_tag()
            self._process_tags(taglist)

        elif t == Gst.MessageType.STATE_CHANGED:
            if message.src == self.playbin:
                old_state, new_state, pending = message.parse_state_changed()
                # Could emit more granular state changes here if needed

    def _process_tags(self, taglist):
        """Process metadata tags from stream."""
        # Common tag names for internet radio:
        # - 'title': Current song/show title (ICY metadata)
        # - 'organization': Station name
        # - 'genre': Music genre
        # - 'bitrate': Stream bitrate

        # Extract title (now playing)
        success, title = taglist.get_string('title')
        if success and title:
            if self.current_title != title:
                self.current_title = title
                self.emit('metadata-changed', 'title', title)

        # Extract organization (sometimes has station name)
        success, org = taglist.get_string('organization')
        if success and org:
            self.emit('metadata-changed', 'organization', org)

        # Extract genre
        success, genre = taglist.get_string('genre')
        if success and genre:
            self.emit('metadata-changed', 'genre', genre)

        # Extract bitrate (in bits per second)
        success, bitrate = taglist.get_uint('bitrate')
        if success and bitrate:
            # Convert to kbps
            bitrate_kbps = bitrate // 1000
            if self.current_bitrate != bitrate_kbps:
                self.current_bitrate = bitrate_kbps
                self.emit('metadata-changed', 'bitrate', str(bitrate_kbps))

        # Also check for nominal-bitrate (some streams use this)
        success, nominal = taglist.get_uint('nominal-bitrate')
        if success and nominal and not self.current_bitrate:
            bitrate_kbps = nominal // 1000
            self.current_bitrate = bitrate_kbps
            self.emit('metadata-changed', 'bitrate', str(bitrate_kbps))

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        self.playbin.set_state(Gst.State.NULL)


# Register the Player class with GObject type system
GObject.type_register(Player)
