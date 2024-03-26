import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import CSVDataSource
from time import time

KYIV_LAT = 50.4501
KYIV_LON = 30.5234
ZOOM = 11
UPD_GAP = 0.01

class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        # додати необхідні змінні
        self.src = CSVDataSource(user_id=1, GPS_src = "./output.csv")
        self.map_layer = LineMapLayer()
        self.car_marker = MapMarker(lat=KYIV_LAT, lon=KYIV_LON, source="images/car.png")
        self.added_markers = []


    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.mapview.add_layer(self.map_layer, mode="scatter")
        Clock.schedule_interval(self.update, UPD_GAP)



    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        if self.src.iter >= (self.src.iter_max-1):
            self.purge_event()
            self.src.iter = 0
        data = self.src.get_new_points()
        for point in data:
            self.map_layer.add_point([point.latitude,point.longitude])
        if point.road_state not in ["OK","Perfect","Normal"]:
            if point.y<0:
                self.set_pothole_marker(point=[point.latitude,point.longitude])
            else:
                self.set_bump_marker(point=[point.latitude,point.longitude])
        self.update_car_marker([point.latitude,point.longitude])
    
    def purge_event(self):
        self.mapview.remove_layer(self.map_layer)
        self.map_layer = LineMapLayer()
        self.mapview.add_layer(self.map_layer, mode="scatter")
        for i in self.added_markers:
            self.mapview.remove_widget(i)


    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.mapview.remove_widget(self.car_marker)
        self.car_marker = MapMarker(lat=point[0], lon=point[1], source="images/car.png")
        self.mapview.add_widget(self.car_marker)
        

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        self.added_markers.append(MapMarker(lat=point[0], lon=point[1], source="images/pothole.png"))
        self.mapview.add_widget(self.added_markers[-1])

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        self.added_markers.append(MapMarker(lat=point[0], lon=point[1], source="images/bump.png"))
        self.mapview.add_widget(self.added_markers[-1])

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView(zoom = ZOOM,lat=KYIV_LAT,lon=KYIV_LON)
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
