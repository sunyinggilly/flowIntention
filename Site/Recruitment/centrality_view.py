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

def build_nodes_links(cg, vertices, edge_df, ctx, loged=False):
    min_w, max_w = 1e10, -1e10
    links, nodes = [], []
    for place_id in vertices: # [北京市, x, y]
        # print(fabs(cg.Vw[place_id]) * ctx['size'])C
        x, y = cg.loc_ll[place_id]
        val = max(0, cg.Vw[place_id])
        sz = val
        # sz = log(val) + 10 if loged else val
        if (ctx['centrality'] in dct_range_bounds) and loged:
            range_bounds = dct_range_bounds[ctx['centrality']]
            sz = 0
            for i, r in enumerate(range_bounds):
                if val > r:
                    sz = i
            sz += 1

        # print(cg.places[place_id], round(cg.Vw[place_id], 4), int(sz * ctx['size']))
        color_lst = ['#5767C9', '#7BD575', '#FFC849', '#FF4D5D', '#5FC2E1', '#00AA73']
        itemStyle = {'color': color_lst[level_dct[cg.places[place_id]]] if cg.places[place_id] in level_dct else color_lst[5]}
        nodes.append({'name': cg.places[place_id], 'value': [x, y, round(cg.Vw[place_id], 4)], 'symbolSize': int(sz * ctx['size']), 'itemStyle': itemStyle})
        # nodes.append({'name': cg.places[place_id], 'x': x, 'y': y, 'value': cg.Vw[place_id], 'symbolSize': int(fabs(cg.Vw[place_id]) * ctx['size'])})
        min_w = min(min_w, cg.Vw[place_id])
        max_w = max(max_w, cg.Vw[place_id])

    for p_from, p_to in edge_df[['from', 'to']].values.tolist():
        ele = {"fromName": cg.places[p_from], "toName": cg.places[p_to], "coords":[cg.loc_ll[p_from], cg.loc_ll[p_to]]}
        links.append(ele)
    
    ctx['min_w'] = min_w
    ctx['max_w'] = max_w
    ctx['nodes'] = nodes
    ctx['links'] = links

    # print(nodes)
    # print(links)
    return


def build_paints(cg, vertices, edge_df, ctx):
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


def build_ctx(request, ctx, type='graph'):
    ctx['coarse_lst'] = ['city', 'province']

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        ctx['coarse'] = request.POST['Coarse']
        ctx['time'] = request.POST['Time']
        if type == 'graph':
            ctx['size'] = float(request.POST['Size'])
            ctx['threshold'] = int(request.POST['Threshold'])
        ctx['centrality'] = request.POST['Centrality']
        if type == 'graph':
            ctx['logged'] = request.POST['Log']
    df_graph, df_centrality, centrality_list, _, _, time_stamps = get_data(coarse=ctx['coarse'], graph_name=ctx['graph_name'])
    # if ctx['graph_name'] == 'all':
        # print(df_graph)

    ctx['centrality_lst'] = centrality_list
    ctx['time_lst'] = time_stamps
    # print(ctx['time_lst'])

    cg = get_graph(df_graph, ctx['time'])
    df_centrality = df_centrality[df_centrality['time'] == ctx['time']]
    
    # 过滤权重
    edge_df, vertices = cg.filter_by_edgeweight(ctx['threshold'])

    # 选择中心度
    set_centrality(cg, df_centrality, centrality=ctx['centrality'])
    
    if type == 'graph':
        build_nodes_links(cg, vertices, edge_df, ctx, True if ctx['logged'] == 'true' else False)
        return render(request, 'centrality-graph.html', ctx)
    else:
        build_paints(cg, vertices, edge_df, ctx)
        return render(request, 'centrality-paint.html', ctx)


def init_page_month(request):
    ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 500, 'time': '201910', 'size': 4, 'centrality': 'pr', 'graph_name': 'month'}
    return build_ctx(request, ctx, 'graph')


def init_page_season(request):
    ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 500, 'time': '2019Q4', 'size': 4, 'centrality': 'pr', 'graph_name': 'season'}
    return build_ctx(request, ctx, 'graph')


def init_page_all(request):
    ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 500, 'time': 'all', 'size': 4, 'centrality': 'pr', 'graph_name': 'all'}
    return build_ctx(request, ctx, 'graph')


def init_page_paint_month(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '201910', 'centrality': 'pr', 'graph_name': 'month'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '2019Q4', 'centrality': 'pr', 'graph_name': 'season'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_all(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': 'all', 'centrality': 'pr', 'graph_name': 'all'}
    return build_ctx(request, ctx, 'paint')
