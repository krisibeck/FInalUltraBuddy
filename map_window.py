import sys

from kivy.clock import Clock
from kivy.properties import ObjectProperty, partial
from kivy_garden.mapview import MapMarkerPopup, MapMarker
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from station_view import Station


class MapWindow(MDScreen):
    """The map window displays the MapView with route points, stations and gps blinker."""

    main_map = ObjectProperty(None)
    blinker = ObjectProperty(None)
    plotting_points_timer = None

    def __init__(self, **kwargs):
        super(MapWindow, self).__init__(**kwargs)
        self.plotted_route_points = set()
        self.station_views = []
        self.points = None
        self.runner_path = []
        self.start_plotting_points_in_fov()
        self.app = MDApp.get_running_app()


    def add_station_views_from_station_models(self):
        for st_model in self.app.map_model.model_stations:
            st_view = Station(st_model)
            st_model.add_observer(st_view)
            self.station_views.append(st_view)
            self.main_map.add_widget(st_view)
            btn_callback = partial(self.popup_station_and_zoom, st_view)
            st_view.btn.bind(on_touch_down=btn_callback)

    def popup_station_and_zoom(self, st_touched, source, touch):
        if source.collide_point(*touch.pos):
            # print(st.name, source, touch)
            for station in self.station_views:
                if station != st_touched and station.is_open:
                    station.refresh_open_status()
            if st_touched.model.dist_diff:
                display_dist = '+' + str(round(st_touched.model.dist_diff, 1)) \
                    if st_touched.model.dist_diff >= 0\
                    else str(round(st_touched.model.dist_diff, 1))
                st_touched.btn.text = st_touched.model.name + '\n' + f'{display_dist} km'
            self.main_map.center_on(st_touched.model.lat, st_touched.model.lon)
            self.main_map.zoom = 12

    # def get_track_points(self):
    #     app = MDApp.get_running_app()
    #     app.cursor.execute("SELECT latitude, longitude, elevation, distance FROM vitosha100 WHERE st_name is NULL")
    #     self.points = app.cursor.fetchall()

    # def get_stations(self):
    #     app = MDApp.get_running_app()
    #     app.cursor.execute("SELECT * FROM vitosha100 WHERE st_name is NOT NULL")
    #     return app.cursor.fetchall()


    # def get_closest_point_on_track(self, gps_lat, gps_lon):
    #     # TODO use self.runner_path to check if it's the end or the start of the race?
    #     min_diff = sys.maxsize
    #     closest_point = None
    #     # print(self.points)
    #     for point in self.points:
    #         diff = abs(point[0] - gps_lat) + abs(point[1] - gps_lon)
    #         if diff < min_diff:
    #             min_diff = diff
    #             closest_point = point
    #     self.runner_path.append(closest_point)
    #     # print('runner path', self.runner_path)
    #     # print(closest_point)
    #     return closest_point

    # def pin_stations(self):
    #     """Pins the stations along the route and saves them as a list of Station() objects in self.stations"""
    #
    #     for station in self.get_stations():
    #         st_lat, st_lon, elev, dist, st_name = station
    #         st = Station(st_name, elev, dist, 0, lat=st_lat, lon=st_lon)
    #         self.stations.append(st)
    #         self.main_map.add_widget(st)
    #         btn_callback = partial(self.popup_station_and_zoom, st)
    #         st.btn.bind(on_touch_down=btn_callback)

    def start_plotting_points_in_fov(self):
        """Called on_zoom of MapView - wait 1 second before starting to plot waypoints
         to avoid doing it constantly if the user is zooming in and out a lot."""

        try:
            # if the timer is not None (i.e. it is counting down from a previous on_zoom), stop the timer, so it can be reset
            self.plotting_points_timer.cancel()
        except:
            # If the timer IS None, canceling it won't work - just leave it alone
            pass

        # when the 1 second has passed without the timer getting cancelled, call the function that will plot the points
        # .schedule_once() schedules only 1 execution of the function as the name suggest
        self.plotting_points_timer = Clock.schedule_once(self.plot_points_in_fov, 1)

    def plot_points_in_fov(self, clock):
        # print(f'{clock} since self.getting_waypoints_timer was set (should be ~ 1 sec)')
        # print(f'Current zoom is: {self.main_map.zoom}')
        # print(f'The four corners of the map are: {self.main_map.get_bbox()}')
        # print('Plotting waypoints now...')

        step = 40
        if 10 <= self.main_map.zoom < 12:
            step = 40
        elif 12 <= self.main_map.zoom < 14:
            step = 30
        elif 14 <= self.main_map.zoom < 16:
            step = 20
        elif 16 <= self.main_map.zoom < 18:
            step = 10
        elif self.main_map.zoom >= 18:
            step = 1

        # self.plotted_route_points.clear()

        min_lat, min_lon, max_lat, max_lon = self.main_map.get_bbox()

        for i in range(0, len(self.app.map_model.points), step):
            p = self.app.map_model.points[i]
            lat, lon = p[0], p[1]
            if p not in self.plotted_route_points and min_lat < lat < max_lat and min_lon < lon < max_lon:
                point = MapMarker(lat=p[0], lon=p[1], source='img/smaller_black_waypoint.png')
                self.plotted_route_points.add(point)
                self.main_map.add_marker(point)

    def respond_to_model_update(self):
        new_lat, new_lon = self.app.map_model.runner_path[-1][:2]
        self.blinker.lat = new_lat
        self.blinker.lon = new_lon


    # def get_closest_station_info(self):
    #     runner = self.runner_path[-1]
    #     until_end = self.points[-1][3] - runner[3]
    #     min_dist = 100
    #     closest_station = None
    #     next_station = [station for station in self.stations if station.dist_diff > 0][0]
    #     for station in self.stations:
    #         if abs(station.dist_diff) < min_dist:
    #             min_dist = abs(station.dist_diff)
    #             closest_station = station
    #     in_between_points = [point for point in self.points if runner[3] < point[3] < next_station.dist]
    #     elev_gain = 0
    #     elev_loss = 0
    #     for i in range(len(in_between_points) - 1):
    #         diff = in_between_points[i + 1][2] - in_between_points[i][2]
    #         if diff < 0:
    #             elev_loss += diff
    #         else:
    #             elev_gain += diff
    #     return {'next': next_station,
    #             'closest': closest_station,
    #             'gain': elev_gain,
    #             'loss': elev_loss,
    #             'end': until_end}