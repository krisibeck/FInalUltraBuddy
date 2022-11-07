from kivy_garden.mapview import MapMarkerPopup
from kivymd.uix.button import MDFlatButton


class Station(MapMarkerPopup):
    def __init__(self, name, elev, dist, dist_diff, **kwargs):
        super(Station, self).__init__(**kwargs)
        self.name = name
        self.elev = elev
        self.dist = dist
        self.dist_diff = dist_diff
        self.btn = MDFlatButton(text=f'See\n{self.name}',
                                font_style='Button',
                                theme_text_color='Custom',
                                text_color='white',
                                md_bg_color='green',
                                valign='center',
                                halign='center')
        self.add_widget(self.btn)

    def update_station_dist_diff_from_runner(self, runner_point):
        self.dist_diff = self.dist - runner_point[3]