import sqlite3
import configparser

from kivy.core.window import Window
from kivymd.app import MDApp

from gpshelper import GpsHelper


# Uncomment to emulate phone dimensions in Desktop app
Window.size = (375, 750)

class UltraBuddyApp(MDApp):
    """This is THE MDApp with build, on_start, on_pause, and on_resume methods.
    The kv file for it must be named with same name without 'App' - 'ultrabuddy'."""

    def build(self):
        """Builds app from ultrabuddy.kv"""
        pass

    def on_start(self):
        """Read configs, apply theme, connect to DB, get route points and stations, initiate GPS service."""

        # Read configs
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read('config.ini')
        # print(self.config['raceresult']['url'])

        # Apply theme
        self.theme_cls.primary_palette = 'LightGreen'
        self.theme_cls.primary_hue = '700'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = 'M3'

        # Connect to DB
        self.connection = sqlite3.connect('ultra_buddy2.db')
        self.cursor = self.connection.cursor()

        # Get route points and stations
        app = MDApp.get_running_app()
        app.root.map_w.get_track_points()
        app.root.map_w.pin_stations()

        # Initiate GPS
        print('***App starting - starting GPS...')
        self.gps_helper = GpsHelper()
        self.gps_helper.run()

    def on_pause(self):
        # Stop GPS on App pause
        print('***App  paused - stopping GPS****')
        self.gps_helper.stop()
        return True

    def on_resume(self):
        # Start GPS on App resume
        print('***App resuming - resuming GPS...***')
        self.gps_helper.resume()


if __name__ == '__main__':
    # start app
    UltraBuddyApp().run()
