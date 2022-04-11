import folium
from openrouteservice import client
import fiona as fn
from shapely.geometry import Polygon, mapping, MultiPolygon, LineString, Point
from shapely.ops import cascaded_union,unary_union
import pyproj
import osmnx as ox

# insert your ORS api key
api_key = '5b3ce3597851110001cf62489766727e63d84f6e8e2ea2b05ec3930f'
ors = client.Client(key=api_key)

# COVID-19 data from SZ government
hotpoints_file = 'high_risk_point.geojson'


# Function to create buffer around hotpoints geometries and transform it to the needed coordinate system (WGS84)
def CreateBufferPolygon(point_in, resolution=2, radius=500):
    sr_wgs = pyproj.Proj(init='epsg:4326')  # WGS84
    sr_utm = pyproj.Proj(init='epsg:32632')  # UTM32N
    point_in_proj = pyproj.transform(sr_wgs, sr_utm, *point_in)  # Unpack list to arguments
    point_buffer_proj = Point(point_in_proj).buffer(radius, resolution=resolution)  # 1000 m buffer
    # Iterate over all points in buffer and build polygon
    poly_wgs = []
    for point in point_buffer_proj.exterior.coords:
        poly_wgs.append(pyproj.transform(sr_utm, sr_wgs, *point))  # Transform back to WGS84
    return poly_wgs


# Function to request directions with avoided_polygon feature
def CreateRoute(avoided_point_list, n=0):
    route_request = {'coordinates': coordinates,
                     'format_out': 'geojson',
                     'profile': 'driving-car',
                     'preference': 'shortest',
                     'instructions': False,
                     'options': {'avoid_polygons': mapping(MultiPolygon(avoided_point_list))}}
    route_directions = ors.directions(**route_request)
    return route_directions


# Function to create buffer around requested route
def CreateBuffer(route_directions):
    line_tup = []
    for line in route_directions['features'][0]['geometry']['coordinates']:
        tup_format = tuple(line)
        line_tup.append(tup_format)
    new_linestring = LineString(line_tup)
    dilated_route = new_linestring.buffer(1)
    return dilated_route

map_SZ = folium.Map(tiles='OpenStreetMap', location=([22.54475,114.05609]), zoom_start=14,control_scale=True)  # Create map


def style_function(color):  # To style data
    return lambda feature: dict(color=color)


counter = 0
COVID_hotpoints = []  # COVID-19 affected regions
hotpoints_geometry = []  # Simplify geometry of hotpoints buffer polygons
with fn.open(hotpoints_file, 'r') as hp_data:  # Open data in reading mode
    print('{} hotpoints in total available.'.format(len(hp_data)))
    for data in hp_data:
        folium.Marker(list(reversed(data['geometry']['coordinates'])),
                          icon=folium.Icon(color='lightgray',
                                           icon_color='red',
                                           icon='twitter',
                                           prefix='fa'),
                          popup=data['properties']['name']).add_to(map_SZ)
        # Create buffer polygons around affected sites with 500 m radius and low resolution
        COVID_hotpoint = CreateBufferPolygon(data['geometry']['coordinates'],
                                              resolution=2, 
                                              radius=500)
        COVID_hotpoints.append(COVID_hotpoint)
        # Create simplify geometry and merge overlapping buffer regions
        poly = Polygon(COVID_hotpoint)
        hotpoints_geometry.append(poly)
#union_poly = mapping(cascaded_union(hotpoints_geometry))
union_poly = mapping(unary_union(hotpoints_geometry))

folium.features.GeoJson(data=union_poly,
                        name='COVID-19 affected areas',
                        style_function=style_function('#ffd699'), ).add_to(map_SZ)

print(len(COVID_hotpoints), 'COVID-19 hotpoints information available.')

# map_tweet.save(os.path.join('results', '1_tweets.html'))
map_SZ
map_SZ.save("map_1.html")


# Visualize start and destination point on map
#orig = ox.distance.nearest_nodes(map_tweet, X=114.01759, Y=22.53652)
#dest = ox.distance.nearest_nodes(G, X=114.08723, Y=22.55193)
coordinates = [[114.0415,22.5596], [114.05460,22.52222]]  # 高尔夫俱乐部 and 皇岗公园
for coord in coordinates:
    folium.map.Marker(list(reversed(coord))).add_to(map_SZ)
map_SZ.save("map_2.html")

# Regular Route
avoided_point_list = []  # Create empty list with avoided HOTPOINTS

import requests
#from requests.adapters import HTTPAdapter
#from requests.packages.urllib3.util.retry import Retry
#session = requests.Session()
#retry = Retry(connect=3, backoff_factor=0.5)
#adapter = HTTPAdapter(max_retries=retry)
#session.mount('http://', adapter)
#session.mount('https://', adapter)
#session.get(url)

requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False

route_directions = CreateRoute(avoided_point_list)  # Create regular route with still empty avoided_point_list

popup_route = "<h4>{0} route</h4><hr>" \
              "<strong>Duration: </strong>{1:.1f} mins<br>" \
              "<strong>Distance: </strong>{2:.3f} km"
distance, duration = route_directions['features'][0]['properties']['summary'].values()
popup = folium.map.Popup(popup_route.format('Regular Route', duration / 60, distance / 1000))
folium.features.GeoJson(data=route_directions,
                        name='Regular Route',
                        style_function=style_function('#ff5050'),
                        overlay=True).add_child(popup).add_to(map_SZ)
print('Generated regular route.')
map_SZ.save("map_3.html")

# Avoiding tweets route
dilated_route = CreateBuffer(route_directions)  # Create buffer around route

# Check if COVID-19 affected hotpoint is located on route
try:
    for site_poly in COVID_hotpoints:
        poly = Polygon(site_poly)
        if poly.within(dilated_route):
            avoided_point_list.append(poly)
            # Create new route and buffer
            route_directions = CreateRoute(avoided_point_list, 1)
            dilated_route = CreateBuffer(route_directions)
    distance, duration = route_directions['features'][0]['properties']['summary'].values()
    popup = folium.map.Popup(popup_route.format('Diesel Route', duration / 60, distance / 1000))
    folium.features.GeoJson(data=route_directions,
                            name='Alternative Route',
                            style_function=style_function('#006600'),
                            overlay=True).add_child(popup).add_to(map_SZ)
    print('Generated alternative route, which avoids affected areas.')
except Exception:
    print('Sorry, there is no route available between the requested destination because of too many blocked streets.')
map_SZ.save("map_4.html")
# map_tweet.save(os.path.join('results', '2_routes.html'))
map_SZ.add_child(folium.map.LayerControl())
map_SZ.save("map_5.html")

