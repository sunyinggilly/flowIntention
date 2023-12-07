import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
import pandas as pd
import pickle
from django.shortcuts import render
from math import fabs
from Functions.ColorGen import ColorGen, ncolors
from CoordGraph import CoordGraph, build_graph
from CONFIG import *
from random import randint as ri
from Functions.ColorGen import random_color
from Functions.read_graph import data_all, get_data, df_loc


def get_graph(df_graph, time, normalize=False):
    # ---------------------------------------------- 建立graph -----------------------------------------------------------------
    df_graph = df_graph[df_graph['time'] == time][['from', 'to', 'count']]
    cg = build_graph(df_graph, df_loc, places=None, normalize=normalize)
    return cg 


def set_cluster(cg, df_cluster, time, cluster_name):
    # ---------------------------------------------- 设置染色 --------------------------------------------------------------------
    df_cluster['name'] = df_cluster['name'].apply(lambda x: cg.get_id(x)).astype(int)
    df_cls = df_cluster[df_cluster['time'] == time]
    colors = [-1] * len(cg.places)
    for u, cid in df_cls[['name', cluster_name]].values.tolist():
        colors[int(u)] = cid
    cg.set_colors(colors)
    return cg


# color_rgb = ncolors(25) '#4500dbff',

# color_rgb = ['#ff0000ff', '#00ff00ff', '#0000ffff', '#ff00ffff', '#7ccaffff', '#7c741dff', '#ffff00ff', '#eb807aff', '#1d807aff', '#95CACA', 
#              '#5f3c23ff', '#bed742ff', '#7c74dbff', '#121a2aff', '#80ffb1ff', '#f3cdeeff', '#FF9224'] + [random_color() for i in range(32)]

color_rgb = ['#ff0000ff', '#00ff00ff', '#0000ffff', '#ff00ffff', '#7ccaffff', '#7c741dff', '#ffff00ff', '#eb807aff', '#1d807aff', '#95CACA', 
             '#5f3c23ff', '#bed742ff', '#d3d7d4ff', '#7c74dbff', '#80ffb1ff', '#f3cdeeff', '#FF9224'] + [random_color() for i in range(32)]

def build_paints_with_nodes_links(cg, vertices, edge_df, ctx):
    links, nodes = [], []
    for place_id in vertices:  # [北京市, x, y]
        if cg.colors[place_id] == -1:
            continue
        x, y = cg.loc_ll[place_id]
        nodes.append({'name': cg.places[place_id], 'value': [x, y]})

    for p_from, p_to, color in edge_df[['from', 'to', 'color']].values.tolist():
#        是否只看相同颜色的
#        if color == -1:
#            continue
        ele = {"fromName": cg.places[p_from], "toName": cg.places[p_to], "coords": [cg.loc_ll[p_from], cg.loc_ll[p_to]]}
        links.append(ele)

    ctx['nodes'] = nodes
    ctx['links'] = links

    grids = []
    # colors_set = set()
    for place_id in vertices: # [北京市, x, y]
        # itemStyle = {'areaColor': color_rgb[cg.colors[place_id]] if cg.colors[place_id] != -1 else '#778899'} 
        # colors_set.add(cg.colors[place_id])
        # grids.append({'name': cg.places[place_id], 'itemStyle': itemStyle, 'value': cg.colors[place_id]})
        grids.append({'name': cg.places[place_id], 'value': cg.colors[place_id]})
        if cg.places[place_id] == '济南市':
            # grids.append({'name': '莱芜市', 'itemStyle': itemStyle, 'value': cg.colors[place_id]})
            grids.append({'name': '莱芜市', 'value': cg.colors[place_id]})
        if cg.places[place_id] == '那曲市':
            # grids.append({'name': '那曲地区', 'itemStyle': itemStyle, 'value': cg.colors[place_id]})
            grids.append({'name': '那曲地区', 'value': cg.colors[place_id]})
        # print(cg.places[place_id])
    ctx['grids'] = grids
    # cates = list(colors_set)
    # cates.sort()
    ctx['categories'] = list(range(len(color_rgb)))
    ctx['color_lst'] = color_rgb
    return ctx


def build_nodes_links(cg, vertices, edge_df, ctx):
    links, nodes = [], []
    for place_id in vertices:  # [北京市, x, y]
        x, y = cg.loc_ll[place_id]
        if cg.places[place_id] in ['三沙市', '台湾省']:
            continue
        itemStyle = {'color': color_rgb[cg.colors[place_id]] if cg.colors[place_id] != -1 and cg.places[place_id] not in ['三沙市', '台湾省'] else '#778899'}    
        print(cg.places[place_id], cg.colors[place_id], color_rgb[cg.colors[place_id]])
        nodes.append({'name': cg.places[place_id], 'value': [x, y], 'itemStyle': itemStyle})
    # 三沙和台湾
    edge_df['color'] = edge_df[['from', 'to', 'color']].apply(lambda x: -1 if cg.places[x[0]] in ['三沙市', '台湾省'] or cg.places[x[1]] in ['三沙市', '台湾省'] else x[2], axis=1)
    for p_from, p_to, color in edge_df[['from', 'to', 'color']].values.tolist():
        if cg.places[p_from] in ['三沙市', '台湾省'] or cg.places[p_to] in ['三沙市', '台湾省']:
            continue
        dct_linestyle = {'color': color_rgb[color] if color != -1 else '#778899'}
        ele = {"fromName":cg.places[p_from], "toName":cg.places[p_to], "coords":[cg.loc_ll[p_from], cg.loc_ll[p_to]], 'lineStyle': dct_linestyle}
        links.append(ele)

    ctx['nodes'] = nodes
    ctx['links'] = links
    return ctx


def build_paints(cg, vertices, edge_df, ctx):
    nodes = []
    for place_id in vertices: # [北京市, x, y]
        itemStyle = {'areaColor': color_rgb[cg.colors[place_id]] if cg.colors[place_id] != -1 else '#778899'}   
        print(cg.places[place_id], cg.colors[place_id], color_rgb[cg.colors[place_id]])
        nodes.append({'name': cg.places[place_id], 'itemStyle': itemStyle, 'value': cg.colors[place_id]})
        if cg.places[place_id] == '济南市':
            nodes.append({'name': '莱芜市', 'itemStyle': itemStyle})
        if cg.places[place_id] == '那曲市':
            nodes.append({'name': '那曲地区', 'itemStyle': itemStyle})
        # print(cg.places[place_id])
    ctx['nodes'] = nodes
    return


def build_ctx(request, ctx, type='graph'):
    ctx['coarse_lst'] = ['city', 'province']

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        ctx['coarse'] = request.POST['Coarse']
        ctx['time'] = request.POST['Time']
        if type == 'graph' or type == 'paint-graph':
            ctx['threshold'] = float(request.POST['Threshold'])
    
    df_graph, _, _, df_cluster, cluster_list, time_stamps = get_data(coarse=ctx['coarse'], graph_name=ctx['graph_name'])
    # if ctx['coarse'] == 'city':
        # df_blackhole = read_blackhole(ctx['coarse'], 'blackhole', ctx['graph_name']).drop([ 'Lweight', 'Lconnection', 'Ldistance', 'weight'], axis=1)  #  ['name', 'time' , 'cluster'] 
        # cluster_blackhole = df_blackhole.drop(['name', 'time'], axis=1).columns
        # df_cluster = pd.merge(df_cluster, df_blackhole, on=['name', 'time'], how='left').fillna(-1)
        # cluster_list = cluster_list + list(cluster_blackhole)
    for cls_e in cluster_list:
        df_cluster[cls_e] = df_cluster[cls_e].astype(int)

    ctx['cluster_lst'] = cluster_list
    ctx['time_lst'] = time_stamps
    
    if request.POST:
        ctx['cluster'] = request.POST['Cluster']
    else:
        ctx['cluster'] = cluster_list[0]

    cg = get_graph(df_graph, time=ctx['time'], normalize= True if ctx['cluster'].find('norm') != -1 else False)
    df_cluster = df_cluster[df_cluster['time'] == ctx['time']]

    # 选择簇
    cg = set_cluster(cg, df_cluster, cluster_name=ctx['cluster'], time=ctx['time'])
    # 过滤权重
    edge_df, vertices = cg.filter_by_edgeweight(ctx['threshold'], filter_vertices=(type == 'graph'))
        
    if type == 'graph':
        build_nodes_links(cg, vertices, edge_df, ctx)
        return render(request, 'cluster-graph.html', ctx)
    elif type == 'paint':
        build_paints(cg, vertices, edge_df, ctx)
        return render(request, 'cluster-paint.html', ctx)
    else:
        build_paints_with_nodes_links(cg, vertices, edge_df, ctx)
        return render(request, 'cluster-paint-graph.html', ctx)


def init_page_month(request):
    ctx = {'coarse': 'city', 'threshold': 500, 'time': '201910', 'graph_name': 'month'}
    return build_ctx(request, ctx, 'graph')


def init_page_season(request):
    ctx = {'coarse': 'city', 'threshold': 500, 'time': '2019Q4', 'graph_name': 'season'}
    return build_ctx(request, ctx, 'graph')


def init_page_all(request):
    ctx = {'coarse': 'city', 'threshold': 500, 'time': 'all', 'graph_name': 'all'}
    return build_ctx(request, ctx, 'graph')


def init_page_paint_month(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '201910', 'graph_name': 'month'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '2019Q4', 'graph_name': 'season'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_all(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': 'all', 'graph_name': 'all'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_graph_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '2019Q4', 'graph_name': 'season'}
    return build_ctx(request, ctx, 'paint-graph')


def init_page_paint_graph_all(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': 'all', 'graph_name': 'all'}
    return build_ctx(request, ctx, 'paint-graph')
