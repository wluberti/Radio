#!/usr/bin/env python3
"""
PyRadio - Internet Radio Player
Main application entry point.
"""

import sys
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

from pyradio.config import Config
from pyradio.ui.main_window import MainWindow


class PyRadioApplication(Gtk.Application):
    """Main GTK Application class."""

    def __init__(self):
        super().__init__(
            application_id='com.github.pyradio',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.window = None
        self.config = None

    def do_startup(self):
        """Called once on application startup."""
        Gtk.Application.do_startup(self)

        # Initialize configuration
        self.config = Config()

        # Set up application-level actions
        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self.on_quit)
        self.add_action(quit_action)

        # Set up keyboard shortcuts
        self.set_accels_for_action('app.quit', ['<Control>q'])

    def do_activate(self):
        """Called when the application is activated."""
        # Create window if it doesn't exist
        if not self.window:
            self.window = MainWindow(self, self.config)
            self.window.connect('close-request', self.on_window_close)

        # Present the window
        self.window.present()

    def on_window_close(self, window):
        """Handle window close event."""
        if self.window:
            self.window.cleanup()
        return False

    def on_quit(self, action, param):
        """Handle quit action."""
        if self.window:
            self.window.cleanup()
        self.quit()


def main():
    """Main entry point."""
    app = PyRadioApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
