import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities, marker_color='blue'):
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Заливка океанов и континентов
        ax.add_feature(cfeature.OCEAN, color='lightblue')
        ax.add_feature(cfeature.LAND, color='lightgreen')
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, color='lightblue')
        ax.add_feature(cfeature.RIVERS)

        # Собираем координаты всех городов
        lats, lngs = [], []
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                lats.append(lat)
                lngs.append(lng)
                plt.plot([lng], [lat],
                         color=marker_color, linewidth=2, marker='o',
                         transform=ccrs.Geodetic())
                plt.text(lng - 3, lat - 12, city,
                         horizontalalignment='right',
                         transform=ccrs.Geodetic())

        # Настройка области отображения для всех городов
        if lats and lngs:
            min_lat, max_lat = min(lats), max(lats)
            min_lng, max_lng = min(lngs), max(lngs)
            # Добавляем буфер для лучшего отображения
            buffer = 10  # Размер буфера в градусах
            ax.set_extent([min_lng - buffer, max_lng + buffer, min_lat - buffer, max_lat + buffer])

        plt.savefig(path)
        plt.close()

    def draw_distance(self, city1, city2):
        pass

if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
