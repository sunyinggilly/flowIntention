import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
import pandas as pd
import pickle
from django.shortcuts import render
from math import fabs, log
from Functions.ColorGen import ColorGen
from CoordGraph import CoordGraph, build_graph
from Functions.read_graph import data_all, get_data, df_loc
from CONFIG import *
from Utils.util_read import get_level_dict, read_translation


level_dct = get_level_dict()
df_loc['ll_x'] = df_loc['ll_x'].apply(lambda x: round(x, 2))
df_loc['ll_y'] = df_loc['ll_y'].apply(lambda x: round(x, 2))


def get_graph(df_graph, time):

    # ---------------------------------------------- 建立graph -----------------------------------------------------------------
    df_graph = df_graph[df_graph['time'] == time][['from', 'to', 'count']]
    cg = build_graph(df_graph, df_loc, places=None)
    return cg


def set_centrality(cg, df_centrality, centrality='pr'):

    # ----------------------------------------------- 设置点权 -----------------------------------------------------------------
    df_centrality['name'] = df_centrality['name'].apply(lambda x: cg.get_id(x)).astype(int)
    weights = [0] * len(cg.places)
    for u, cid in df_centrality[['name', centrality]].values.tolist():
        if centrality in ['jd_All']:
            cid = max(30000, cid)
        weights[int(u)] = cid
    cg.set_vertex_weight(weights)
    return cg


dct_range_bounds = {'pr': [0.001, 0.002, 0.0035, 0.005, 0.01, 0.015, 0.02, 0.03, 1],
                    'authority': [0.001, 0.002, 0.0035, 0.005, 0.01, 0.015, 0.02, 0.03, 1],
                    'hub': [0.001, 0.003, 0.005, 0.007, 0.009, 0.011, 0.013, 0.015, 0.02, 1]}

def build_paints(cg, vertices, ctx):
    min_w, max_w = 1e10, -1e10
    nodes = []
    for place_id in vertices: # [北京市, x, y]
        if cg.places[place_id] == '济南市':
            nodes.append({'name': '莱芜市', 'value': round(cg.Vw[place_id], 4)})
        if cg.places[place_id] == '那曲市':
            nodes.append({'name': '那曲地区', 'value': round(cg.Vw[place_id], 4)})
        nodes.append({'name': cg.places[place_id], 'value': round(cg.Vw[place_id], 4)})
        min_w = min(min_w, cg.Vw[place_id])
        max_w = max(max_w, cg.Vw[place_id])

    if min_w < 0 and ctx['centrality'].find('jd') == -1:
        x = min(fabs(min_w), fabs(max_w))
        ctx['min_w'] = -x
        ctx['max_w'] = x
        ctx['color_list'] = ['lightskyblue', 'white', 'orangered']
    else:
        ctx['min_w'] = min_w
        ctx['max_w'] = max_w
        ctx['color_list'] = ['white', 'yellow', 'orangered', 'red']
    ctx['nodes'] = nodes
    return


def read_data():
    path = '%s/edu/' % OUT_MISMATCH_PATH
    df_edu_centrality_month = pd.read_csv('%s/centrality/city/month.csv' % path)
    df_edu_centrality_season = pd.read_csv('%s/centrality/city/season.csv' % path)
    df_edu_centrality_all = pd.read_csv('%s/centrality/city/all.csv' % path)
    df_edu_graph_month = pd.read_csv('%s/transition_month.csv' % path)
    df_edu_graph_season = pd.read_csv('%s/transition_season.csv' % path)
    df_edu_graph_all = pd.read_csv('%s/transition_all.csv' % path)
    month_timelist = df_edu_graph_month['time'].drop_duplicates().sort_values().tolist()
    season_timelist = df_edu_graph_season['time'].drop_duplicates().sort_values().tolist()
    all_timelist = df_edu_graph_all['time'].drop_duplicates().sort_values().tolist()
    centrality_list = list(df_edu_centrality_season.drop(['time', 'name', 'value'], axis=1).columns)
    value_list = df_edu_graph_season['value'].drop_duplicates().tolist()
    return (df_edu_graph_month, df_edu_centrality_month, month_timelist), \
           (df_edu_graph_season, df_edu_centrality_season, season_timelist), \
           (df_edu_graph_all, df_edu_centrality_all, all_timelist), \
           centrality_list, value_list 

def get_data(graph_name, val):
    if graph_name == 'month':
        df_graph, df_centrality, time_stamps = data_edu_month[0], data_edu_month[1], data_edu_month[2]
    elif graph_name == 'season':
        df_graph, df_centrality, time_stamps = data_edu_season[0], data_edu_season[1], data_edu_season[2],
    elif graph_name == 'all':
        df_graph, df_centrality, time_stamps = data_edu_all[0], data_edu_all[1], data_edu_all[2],
    df_graph = df_graph[df_graph['value'] == val]
    df_centrality = df_centrality[df_centrality['value'] == val]

    df_graph = df_graph.drop(['province_from', 'province_to'], axis=1)
    df_graph = df_graph.rename(columns={'city_from':'from', 'city_to':'to'})

    return df_graph.drop('value', axis=1), df_centrality.drop('value', axis=1), time_stamps, centrality_list

data_edu_month, data_edu_season, data_edu_all, centrality_list, value_list = read_data()

def build_ctx(request, ctx):
    ctx['coarse_lst'] = ['city', 'province']
    ctx['value_lst'] = value_list

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        ctx['coarse'] = request.POST['Coarse']
        ctx['time'] = request.POST['Time']
        ctx['centrality'] = request.POST['Centrality']
        ctx['value'] = request.POST['Value']
    
    df_graph, df_centrality, time_stamps, centrality_list = get_data(graph_name=ctx['graph_name'], val=ctx['value'])

    ctx['centrality_lst'] = centrality_list
    ctx['time_lst'] = time_stamps

    cg = get_graph(df_graph, ctx['time'])
    df_centrality = df_centrality[df_centrality['time'] == ctx['time']]
    
    # 过滤权重
    _, vertices = cg.filter_by_edgeweight(ctx['threshold'])

    # 选择中心度
    set_centrality(cg, df_centrality, centrality=ctx['centrality'])
    
    build_paints(cg, vertices, ctx)
    return render(request, 'centrality-paint_type.html', ctx)


def init_page_paint_month(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '201910', 'centrality': 'pr', 'graph_name': 'month', 'value': '本科及以上'}
    return build_ctx(request, ctx)


def init_page_paint_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '2019Q4', 'centrality': 'pr', 'graph_name': 'season', 'value': '本科及以上'}
    return build_ctx(request, ctx)

def init_page_paint_all(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': 'all', 'centrality': 'pr', 'graph_name': 'all', 'value': '本科及以上'}
    return build_ctx(request, ctx)

