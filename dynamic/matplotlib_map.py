import geopandas as gpd
roadfile='results/weighted_road.shp'
nodefile='data/nodes.shp'
road_shp=gpd.GeoDataFrame.from_file(roadfile,encoding='utf-8')
node_shp=gpd.GeoDataFrame.from_file(nodefile,encoding='utf-8')

import networkx as nx
G1=nx.from_pandas_edgelist(road_shp,'from_start','to_end',
                         edge_attr=['osmid','w_21'],
                          create_using=nx.DiGraph())
G2=nx.from_pandas_edgelist(road_shp,'from_start','to_end',
                         edge_attr=['osmid','road_lengt'],
                          create_using=nx.DiGraph())

startnode=2319202440
endnode=8869146293
path1=nx.shortest_path(G1,startnode,endnode,weight='w_21')
path2=nx.shortest_path(G2,startnode,endnode,weight='road_lengt')

import pandas as pd
def GetPath(path,road):
    pathroad=pd.DataFrame()
    for i in range(len(path)-1):
        node1=path[i]
        node2=path[i+1]
        #r=road[(road['from_start']==node1)&(road['to_end']==node2)]
        r = road[((road['from_start'] == node1) & (road['to_end'] == node2)) | (road['from_start'] == node2) & (road['to_end'] == node1)]
        pathroad=pathroad.append(r)
    return pathroad

path_road1=GetPath(path1,road_shp)
path_road2=GetPath(path2,road_shp)
path_road1.to_file('results/path_road1.shp', driver='ESRI Shapefile',encoding='utf-8')
path_road2.to_file('results/path_road2.shp', driver='ESRI Shapefile',encoding='utf-8')

def shortest_routin(pathroad):
    shortest_route=list()
    route_len=0
    for j in range(len(pathroad)):
        route=pathroad.iloc[j]['road_lengt']
        shortest_route.append(route)
        for k in shortest_route:
            route_len=route_len+k
    return route_len

length1= shortest_routin(path_road1)  
length2= shortest_routin(path_road2)

import geopandas as gp
import folium
import matplotlib.pyplot as plt
#from cartopy import crs as ccrs
#%matplotlib inline
SZ_road = gp.read_file('results/weighted_road.shp')
hotpoint = gp.read_file('data/futianqu_hotpoint.geojson')

fig, ax = plt.subplots(figsize=(10, 10))
hotpoint.plot(ax=ax,color='orange')
SZ_road.plot(ax=ax, color='cornflowerblue')
path_road1.plot(ax=ax, color='green')
path_road2.plot(ax=ax, color='red')
print(length1)
print(length2)
plt.show()
