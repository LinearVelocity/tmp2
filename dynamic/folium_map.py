import webbrowser as wb
import folium
from folium.plugins import HeatMap, MiniMap, MarkerCluster
#import folium
import numpy as np

# 增加小地图
def draw_minimap(map):
    minimap = MiniMap(toggle_display=True,
                      tile_layer='Stamen Toner',
                      position='topleft',
                      width=100,
                      height=100)
    map.add_child(minimap)

# 在地图上绘制一个小Info标记物
def draw_icon(map, loc):
    mk = folium.features.Marker(loc)
    pp = folium.Popup(str(loc))
    ic = folium.features.Icon(color="pink")
    mk.add_child(ic)
    mk.add_child(pp)
    map.add_child(mk)

# 在地图上绘制无边框圆形，填充颜色
def draw_CircleMarker1(loc, radius, map):
    folium.CircleMarker(
        location=loc,
        radius=radius,
        color="cornflowerblue",
        stroke=False,
        fill=True,
        fill_opacity=0.6,
        opacity=1,
        popup="{} 像素".format(radius),
        tooltip=str(loc),
    ).add_to(map)
    
def draw_CircleMarker2(loc, radius, map):
    folium.CircleMarker(
        location=loc,
        radius=radius,
        color="orange",
        stroke=False,
        fill=True,
        fill_opacity=0.6,
        opacity=1,
        popup="{} 像素".format(radius),
        tooltip=str(loc),
    ).add_to(map)
    
    
def draw_CircleMarker3(loc, radius, map):
    folium.CircleMarker(
        location=loc,
        radius=radius,
        color="red",
        stroke=False,
        fill=True,
        fill_opacity=0.6,
        opacity=1,
        popup="{} 像素".format(radius),
        tooltip=str(loc),
    ).add_to(map)

m = folium.Map(location=[22.54, 114.05], zoom_start=10,control_scale=True)
draw_minimap(m)
import pandas as pd
hotp=pd.read_csv(r'data/futianqu.csv')
region=[]
for i in range(len(hotp)):
    region.append(hotp['location'][i])
for j in range(len(region)) :
    l=eval(region[j])
    l=list(l)
    draw_icon(m, l)
    draw_CircleMarker1(l, 50, m)
    draw_CircleMarker2(l, 30, m)
    draw_CircleMarker3(l, 10, m)

#path1
f1 = open(r'results/path_road1.json',encoding='utf-8').read()
popup=folium.Popup('Covid-19_avoided_route')
folium.GeoJson(f1, name="path_road1_geojson",style_function=lambda x:{'color':'green'}).add_child(popup).add_to(m)
#path2
f2 = open(r'results/path_road2.json',encoding='utf-8').read()
popup=folium.Popup('Covid-19_risk_route')
folium.GeoJson(f2, name="path_road2_geojson",style_function=lambda x:{'color':'red'}).add_child(popup).add_to(m)
#OD
f3=open(r'data/OD.json',encoding='utf-8').read()
folium.GeoJson(f3, name='OD_geojson').add_to(m)
m.save('map.html')
