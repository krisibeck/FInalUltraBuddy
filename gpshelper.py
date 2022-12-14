from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from plyer import gps


class GpsHelper:
    """Controls gps services and actions upon obtaining new gps coordinates."""

    def run(self):
        """Initiated on_start of App - start blinking the gps_blinker, requests permsissions,
        starts collecting gps data every 30 seconds"""
        gps_blinker = App.get_running_app().root.map_w.ids.blinker
        gps_blinker.blink()

        # uncomment to run as desktop app instead of mobile app
        self.update_blinker_position()

        # Request permissions and start gps service on Android
        if platform == 'android':
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                    gps.configure(on_location=self.update_blinker_position,
                                  on_status=self.on_auth_status)
                    gps.start(minTime=30000, minDistance=100)
                else:
                    print("Did not get all permissions")


            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION], callback)

        # Start gps service on iOS
        if platform == 'ios':
            gps.configure(on_location=self.update_blinker_position,
                          on_status=self.on_auth_status)
            gps.start(minTime=30000, minDistance=100)

    def stop(self):
        """Initiated on_pause of App to stop collecting gps data."""
        print('GPS stopped...')
        gps.stop()

    def resume(self):
        """Initiated on_resume of App to start collecting gps data again (no permissions needed)."""
        gps.start(minTime=30000, minDistance=100)

    def update_blinker_position(self, *args, **kwargs):
        # gps_lat = kwargs['lat']
        # gps_lon = kwargs['lon']
        # Can use these hard-coded coordinates for testing
        gps_lat = 42.50049
        gps_lon = 23.206102
        print("GPS POSITION:", gps_lat, gps_lon)
        app = App.get_running_app()

        # Update gps location to closest point on track
        closest_route_point = app.root.map_w.get_closest_point_on_track(gps_lat, gps_lon)
        # print('closet route point:', closest_route_point)
        track_lat, track_lon = closest_route_point[:2]

        # Update GpsBlinker position
        gps_blinker = app.root.map_w.ids.blinker
        gps_blinker.lat = track_lat
        gps_blinker.lon = track_lon

        # Update station distances from runner
        stations = app.root.map_w.stations
        for station in stations:
            station.update_station_dist_diff_from_runner(closest_route_point)
        app.root.next_w.update_next_station()


    def on_auth_status(self, general_status, status_message):
        """Called on_status for gps.configure() - proceed normally if permissions granted, else popup warning Dialog."""
        if general_status == 'provider-enabled':
            pass
        else:
            self.open_gps_access_popup()

    def open_gps_access_popup(self):
        """Dialogue popped up in case of gps persmissions not granted."""
        dialog = MDDialog(title="GPS Error", text="You need to enable GPS access for the app to function properly")
        dialog.size_hint = [.8, .8]
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        dialog.open()
