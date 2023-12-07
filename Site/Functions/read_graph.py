import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
from CONFIG import *
import pandas as pd
from Utils.util_read import read_graph_from_file, read_location
import json
from math import log
import warnings



def read_centrality(coarse, graph_name='month'):

    df = pd.read_csv("%s/%s/centrality/%s_centrality.csv" % (ANA_DATA_PATH, graph_name, coarse))
    
    df_kmeans = pd.read_csv("%s/%s/jd/%s_kmeans.csv" % (ANA_DATA_PATH, graph_name, coarse))
    df = pd.merge(df, df_kmeans, on=['name', 'time'], how='left').fillna(0)
    return df, list(df.drop(['name', 'time'], axis=1).columns)


def read_cluster(coarse, graph_name='month'):
    df = pd.read_csv("%s/%s/clustering/%s_cluster.csv" % (ANA_DATA_PATH, graph_name, coarse))
    return df, list(df.drop(['name', 'time'], axis=1).columns)


def read_dataset(graph_name, coarse):
    df_graph = read_graph_from_file(coarse=coarse, graph_name=graph_name)
    df_centrality, centrality_list = read_centrality(coarse=coarse, graph_name=graph_name)
    df_cluster, cluster_list = read_cluster(coarse=coarse, graph_name=graph_name)
    df_graph['time'] = df_graph['time'].apply(lambda x: str(x))
    df_cluster['time'] = df_cluster['time'].apply(lambda x: str(x))
    df_centrality['time'] = df_centrality['time'].apply(lambda x: str(x))
    time_lst = df_graph['time'].drop_duplicates().sort_values().tolist()
    return df_graph, df_centrality, centrality_list, df_cluster, cluster_list, time_lst


def read_all():
    data_all = {}
    graphs = ['season', 'month', 'all']
    for graph_name in graphs:
        data_all[(graph_name, 'city')] = read_dataset(graph_name, 'city')
        data_all[(graph_name, 'province')] = read_dataset(graph_name, 'province')
    return data_all


def get_data(graph_name, coarse):
    return data_all[(graph_name, coarse)]


def read_wgs_center(coarse='city'):
    json_files = {'province': 'china.json', 'city': 'cities.geojson'}
    with open("%s/city/%s" % (DATA_PATH, json_files[coarse]), 'r') as f:
        city_str = f.readline()
        city_data = json.loads(city_str)['features']

    dct = {}
    for u in city_data:
        city_name = u['properties']['name']
        if city_name == '':
            continue
        city_center = u['properties']['center']
        dct[city_name] = city_center

    return dct

dct_city_wgs = read_wgs_center('city')
dct_province_wgs = read_wgs_center('province')

df_loc_mc = read_location(coord_sys='mc', coarse='km')
df_loc_ll = read_location(coord_sys='ll', coarse=None)
df_loc = pd.merge(df_loc_mc, df_loc_ll, on=['name'])[['name', 'll_x', 'll_y', 'mc_x', 'mc_y']]

data_all = read_all()
