import sys
sys.path.append('/code')
sys.path.append('/code/Site')
import pandas as pd
import pickle
from django.shortcuts import render
from math import fabs, log
from Functions.ColorGen import ColorGen
from CoordGraph import CoordGraph, build_graph
from Functions.read_graph import data_all, get_data, df_loc
from CONFIG import *


df_loc['ll_x'] = df_loc['ll_x'].apply(lambda x: round(x, 2))
df_loc['ll_y'] = df_loc['ll_y'].apply(lambda x: round(x, 2))


def get_graph(df_graph, time):
    # ---------------------------------------------- 建立graph -----------------------------------------------------------------
    df_graph = df_graph[df_graph['time'] == time][['from', 'to', 'count']]
    cg = build_graph(df_graph, df_loc, places=None)
    return cg


def set_centrality(cg, df_centrality, centrality, timebase, timecheck, mode='ratio', threshold=0, use_list=None):
    df_cent_base = df_centrality[df_centrality['time'] == timebase]
    df_cent_base.rename(columns={centrality: 'timebase'}, inplace=True)
    df_cent_check = df_centrality[df_centrality['time'] == timecheck]
    df_cent_check.rename(columns={centrality: 'timecheck'}, inplace=True)
    df_cent_change = pd.merge(df_cent_base, df_cent_check, on='name')

    df_cent_base = df_centrality[df_centrality['time'] == '2019Q4']
    df_cent_base.rename(columns={centrality: '2019Q4'}, inplace=True)
    df_cent_change = pd.merge(df_cent_change, df_cent_base, on='name')

    df_cent_base = df_centrality[df_centrality['time'] == '2020Q4']
    df_cent_base.rename(columns={centrality: '2020Q4'}, inplace=True)
    df_cent_change = pd.merge(df_cent_change, df_cent_base, on='name')
    sum_num = df_cent_change['timebase'].sum()

    df_cent_change[centrality] = df_cent_change[['timebase', 'timecheck']].apply(lambda x: (x[1] - x[0]) / x[0] if x[0] > threshold * sum_num else 0, axis=1)

    if mode != 'ratio' and ((timecheck == '2020Q1' and timebase == '2021Q1') or (timecheck == '2020Q2' and timebase == '2021Q2')):
        print(mode)
        df_cent_change['1pr'] = df_cent_change[['2019Q4', '2020Q4']].apply(lambda x: x[1] / x[0] if x[0] > 0 else 0, axis=1)
        df_cent_change[centrality] = df_cent_change[['timebase', 'timecheck', '1pr']].apply(lambda x: x[1] / x[0] * x[2] - 1 if x[0] * sum_num  else 0, axis=1)

    # ----------------------------------------------- 设置点权 -----------------------------------------------------------------
    df_cent_change['name'] = df_cent_change['name'].apply(lambda x: cg.get_id(x)).astype(int)
    weights = [0] * len(cg.places)
    for u, cid in df_cent_change[['name', centrality]].values.tolist():
        weights[int(u)] = cid if u in use_list else 0
    cg.set_vertex_weight(weights)
    return cg


def build_paints(cg, vertices, ctx):
    min_w, max_w = 1e10, -1e10
    nodes = []
    for place_id in vertices:  # [北京市, x, y]
        if cg.places[place_id] == '济南市':
            nodes.append({'name': '莱芜市', 'value': round(cg.Vw[place_id], 4)})
        if cg.places[place_id] == '那曲市':
            nodes.append({'name': '那曲地区', 'value': round(cg.Vw[place_id], 4)})
        nodes.append({'name': cg.places[place_id], 'value': round(cg.Vw[place_id], 4)})
        min_w = min(min_w, cg.Vw[place_id])
        max_w = max(max_w, cg.Vw[place_id])

    if min_w < 0:
        if max_w > 0:
            x = min(fabs(min_w), fabs(max_w))
        else:
            x = fabs(min_w)
        if ctx['centrality'].find('jd') != -1:
            x = min(x, 3)
        ctx['min_w'] = -x
        ctx['max_w'] = x
        ctx['color_list'] = ['lightskyblue', 'white', 'orangered']
    else:
        ctx['min_w'] = min_w
        ctx['max_w'] = max_w
        ctx['color_list'] = ['white', 'yellow', 'red']
    ctx['nodes'] = nodes
    return


def build_ctx(request, ctx, mode='ratio'):
    ctx['coarse_lst'] = ['city', 'province']
    ctx['region_lst'] = ['YRD', 'BTH', 'PRD']

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        ctx['coarse'] = request.POST['Coarse']
        ctx['timebase'] = request.POST['TimeBase']
        ctx['timecheck'] = request.POST['TimeCheck']
        ctx['centrality'] = request.POST['Centrality']
        ctx['region'] = request.POST['Region']

    df_graph, _, _, _, _, time_stamps = get_data(coarse=ctx['coarse'], graph_name=ctx['graph_name'])
    df_centrality = pd.read_csv('%s/Analysis/RegionAnalysis/out/region_sources.csv' % HOME_PATH)
    print(df_centrality)
    df_centrality = df_centrality[df_centrality['region'] == ctx['region']].drop('region', axis=1)
    centrality_list = list(df_centrality.drop(['name', 'time'], axis=1).columns)
    
    df_use = df_centrality[df_centrality['time'] == '2019Q4']
    df_use = df_use[df_use['count'] > 1000]
    use_list = df_use['name'].drop_duplicates().tolist()
    
    ctx['centrality_lst'] = centrality_list
    ctx['time_lst'] = time_stamps

    cg = get_graph(df_graph, ctx['timecheck'])
    use_list = [int(cg.get_id(u)) for u in use_list]

    # 过滤权重
    edge_df, vertices = cg.filter_by_edgeweight(ctx['threshold'])

    # 选择中心度
    set_centrality(cg, df_centrality, centrality=ctx['centrality'], timebase=ctx['timebase'], timecheck=ctx['timecheck'], 
                   mode=mode, threshold=0.0005, use_list=use_list)

    build_paints(cg, vertices, ctx)
    return render(request, 'centrality-comp-region-paint.html', ctx)


def init_page_paint_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'timebase': '2019Q4', 'timecheck': '2020Q4', 'centrality': 'count', 'graph_name': 'season', 'region': 'BTH'}
    return build_ctx(request, ctx, mode='ratio')

