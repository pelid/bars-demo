from flask import Flask
import flask
import json
from yandex_geocoder import Client
from geopy import distance
import folium


def get_bars_info(current_location):
    with open('data-2897-2019-01-22.json', 'r', encoding='CP1251') as json_file:
        bars = json.load(json_file)

    bars_info = []

    for bar in bars:
        name = bar['Name']
        coordinates = bar['geoData']['coordinates']
        phone = bar['PublicPhone'][0]['PublicPhone']
        bars_info.append({'title': name,
                            'latitude': coordinates[0],
                            'longitude': coordinates[1],
                            'distance': get_distance_to_bar(coordinates, current_location),
                            'phone': phone})

    return bars_info


def get_distance_to_bar(bar_coordinates, current_coordinates):
    return distance.distance(bar_coordinates, current_coordinates).km


def add_marker(bar, bar_map):
    bar_latitude = bar['latitude']
    bar_longitude = bar['longitude']
    bar_title = bar['title']
    bar_distance = f'{bar["distance"]:.2f} km'
    tooltip = f'{bar_title}: {bar_distance}.'
    bar_phone = bar['phone']
    folium.Marker([bar_longitude, bar_latitude],
                          popup=f'<i>Телефон: {bar_phone}.</i>',
                          tooltip=tooltip).add_to(bar_map)


def save_map(nearest_bars, current_location):
    latitude = current_location[1]
    longitude = current_location[0]
    location = [float(latitude), float(longitude)]
    bar_map = folium.Map(location=location, zoom_start=15)
    folium.Marker(location, tooltip='Я тут.', icon=folium.Icon(color='red')).add_to(bar_map)
    for bar in nearest_bars:
        add_marker(bar, bar_map)
    bar_map.save('index.html')


def get_map():
    address = flask.request.args.get('address', 'Москва')
    current_location = Client.coordinates(address)
    bars_info = get_bars_info(current_location)
    number_of_bars = 5
    nearest_bars = sorted(bars_info, key=lambda x: x['distance'])[:number_of_bars]
    save_map(nearest_bars, current_location)

    # TODO заменить обычный файл на in memory аналог, чтобы не было конфликтов при форке
    with open('index.html') as file:
        return file.read()


def main():

    app = Flask(__name__)
    app.add_url_rule('/', 'map', get_map)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()



