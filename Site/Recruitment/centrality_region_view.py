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

trans_dct = read_translation()
trans_dct['泰州市'] = 'Taizhou (泰州)'
trans_dct['台州市'] = 'Taizhou (台州)'
df_loc['ll_x'] = df_loc['ll_x'].apply(lambda x: round(x, 2))
df_loc['ll_y'] = df_loc['ll_y'].apply(lambda x: round(x, 2))


def get_regions(region_name='YRD'):
    if region_name == 'PRD':
        return ['广州市', '佛山市', '肇庆市', '深圳市', '东莞市', '惠州市', '珠海市', '中山市', '江门市']
    elif region_name == 'BTH':
        return ['北京市', '天津市', '保定市', '廊坊市', '唐山市', '石家庄市', '邯郸市', '秦皇岛市', '张家口市', '承德市', 
                '沧州市', '邢台市', '衡水市', '定州市', '辛集市']
    elif region_name == 'YRD':
        return ['上海市', '南京市', '无锡市', '常州市', '苏州市', '南通市', '盐城市', '扬州市', '镇江市', '泰州市', '杭州市',
                '宁波市', '嘉兴市', '湖州市', '绍兴市', '金华市', '舟山市', '台州市', '合肥市', '芜湖市', '马鞍山市', '铜陵市', '安庆市',
                '滁州市', '池州市', '宣城市']


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
        weights[int(u)] = cid
    # print(weights)
    cg.set_vertex_weight(weights)
    # print(cg.Vw)
    return cg

def read_tier_dct():
    df = pd.read_csv()


dct_range_bounds = {'pr': [0.001, 0.002, 0.0035, 0.005, 0.01, 0.015, 0.02, 0.03, 1],
                    'authority': [0.001, 0.002, 0.0035, 0.005, 0.01, 0.015, 0.02, 0.03, 1],
                    'hub': [0.001, 0.003, 0.005, 0.007, 0.009, 0.011, 0.013, 0.015, 0.02, 1]}

tier_dct = get_level_dict()
# print(tier_dct)
def build_nodes_links(cg, vertices, edge_df, ctx, loged=False):
    links, nodes = [], []
    for place_id in vertices:
        x, y = cg.loc_ll[place_id]
        val = max(0, cg.Vw[place_id])
        sz = val
        if (ctx['centrality'] in dct_range_bounds) and loged:
            range_bounds = dct_range_bounds[ctx['centrality']]
            sz = 0
            for i, r in enumerate(range_bounds):
                if val > r:
                    sz = i
            sz += 1
        # nodes.append({'name': cg.places[place_id], 'x': x, 'y': y, 'category': tier_dct[cg.places[place_id]]})
        nodes.append({'name': trans_dct[cg.places[place_id]], 'x': x, 'y': -y, 'category': tier_dct[cg.places[place_id]], 'symbolSize': int(sz * ctx['size'])})
        # nodes.append({'name': cg.places[place_id], 'x': x, 'y': y, 'value': round(cg.Vw[place_id], 4), 'symbolSize': int(sz * ctx['size'])})

    for p_from, p_to in edge_df[['from', 'to']].values.tolist():
        # lineStyle = {'curveness': 1}
        # ele = {"source": cg.places[p_from], "target": cg.places[p_to], "lineStyle": lineStyle}
        ele = {"source": trans_dct[cg.places[p_from]], "target": trans_dct[cg.places[p_to]]}
        links.append(ele)
    ctx['nodes'] = nodes
    ctx['links'] = links
    # print(nodes)
    # print(links)
    return

def build_nodes_links2(cg, vertices, edge_df, ctx, loged=False):
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
        itemStyle = {'color': color_lst[tier_dct[cg.places[place_id]]] if cg.places[place_id] in tier_dct else color_lst[5]}
        nodes.append({'name': trans_dct[cg.places[place_id]], 'value': [x, y, round(cg.Vw[place_id], 4)], 'symbolSize': int(sz * ctx['size']), 'itemStyle': itemStyle})
        # nodes.append({'name': cg.places[place_id], 'x': x, 'y': y, 'value': cg.Vw[place_id], 'symbolSize': int(fabs(cg.Vw[place_id]) * ctx['size'])})

    links = [[], [], [], [], [], []]
    for p_from, p_to in edge_df[['from', 'to']].values.tolist():
        id = tier_dct[cg.places[p_from]]
        ele = {"fromName": trans_dct[cg.places[p_from]], "toName": trans_dct[cg.places[p_to]], "coords":[cg.loc_ll[p_from], cg.loc_ll[p_to]]}
        links[id].append(ele)

    ctx['nodes'] = nodes
    ctx['links0'] = links[0]
    ctx['links1'] = links[1]
    ctx['links2'] = links[2]
    ctx['links3'] = links[3]
    ctx['links4'] = links[4]
    ctx['links5'] = links[5]
    return

def build_paints(cg, vertices, edge_df, ctx):
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
    # print(min_w, max_w)
    ctx['min_w'] = min_w
    ctx['max_w'] = max_w
    ctx['color_list'] = ['white', 'yellow', 'orangered', 'red']
    ctx['nodes'] = nodes
    return




def build_ctx2(request, ctx, type='graph'):
    ctx['region_lst'] = ['YRD', 'BTH', 'PRD']
    ctx['coarse_lst'] = ['city']

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        # ctx['time'] = request.POST['Time']
        if type == 'graph':
            ctx['size'] = float(request.POST['Size'])
            ctx['threshold'] = int(request.POST['Threshold'])
        ctx['centrality'] = request.POST['Centrality']
        ctx['region'] = request.POST['Region']
        if type == 'graph':
            ctx['logged'] = 'true'  # request.POST['Log']

    rcities = get_regions(ctx['region'])

    df_graph, df_centrality, centrality_list, _, _, time_stamps = get_data(coarse='city', graph_name=ctx['graph_name'])
    df_centrality = df_centrality[df_centrality['name'].isin(rcities)]
    df_graph = df_graph[df_graph['from'].isin(rcities) & df_graph['to'].isin(rcities)]

    centrality_list = list(df_centrality.drop(['name', 'time'], axis=1).columns)
    ctx['centrality_lst'] = centrality_list
    ctx['time_lst'] = time_stamps

    cg = get_graph(df_graph, ctx['time'])
    df_centrality = df_centrality[df_centrality['time'] == ctx['time']]

    # 过滤权重
    edge_df, vertices = cg.filter_by_edgeweight(ctx['threshold'])
    # print(vertices)

    # 选择中心度
    set_centrality(cg, df_centrality, centrality=ctx['centrality'])
    
    if type == 'graph':
        build_nodes_links2(cg, vertices, edge_df, ctx, True if ctx['logged'] == 'true' else False)
        return render(request, 'centrality-region-graph_1025.html', ctx)
    else:
        build_paints(cg, vertices, edge_df, ctx)
        return render(request, 'centrality-region-paint.html', ctx)

def build_ctx(request, ctx, type='graph'):
    ctx['region_lst'] = ['YRD', 'BTH', 'PRD']
    ctx['coarse_lst'] = ['city']

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        # ctx['time'] = request.POST['Time']
        if type == 'graph':
            ctx['size'] = float(request.POST['Size'])
            print(ctx['size'])
            ctx['threshold'] = int(request.POST['Threshold'])
        ctx['centrality'] = request.POST['Centrality']
        ctx['region'] = request.POST['Region']
        if type == 'graph':
            ctx['logged'] = 'true'  # request.POST['Log']

    rcities = get_regions(ctx['region'])

    df_graph, df_centrality, centrality_list, _, _, time_stamps = get_data(coarse='city', graph_name=ctx['graph_name'])
    df_centrality = df_centrality[df_centrality['name'].isin(rcities)]
    df_graph = df_graph[df_graph['from'].isin(rcities) & df_graph['to'].isin(rcities)]

    centrality_list = list(df_centrality.drop(['name', 'time'], axis=1).columns)
    ctx['centrality_lst'] = centrality_list
    ctx['time_lst'] = time_stamps

    cg = get_graph(df_graph, ctx['time'])
    df_centrality = df_centrality[df_centrality['time'] == ctx['time']]

    # 过滤权重
    edge_df, vertices = cg.filter_by_edgeweight(ctx['threshold'])
    # print(vertices)

    # 选择中心度
    set_centrality(cg, df_centrality, centrality=ctx['centrality'])
    
    if type == 'graph':
        build_nodes_links(cg, vertices, edge_df, ctx, True if ctx['logged'] == 'true' else False)
        return render(request, 'centrality-region-graph.html', ctx)
    else:
        build_paints(cg, vertices, edge_df, ctx)
        return render(request, 'centrality-region-paint.html', ctx)


# def init_page_month(request):
#     ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 500, 'time': '201910', 'size': 4, 'centrality': 'authority', 'graph_name': 'month', 'region': 'BTH'}
#     return build_ctx(request, ctx, 'graph')


# def init_page_season(request):
#     ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 500, 'time': '2019Q4', 'size': 4, 'centrality': 'authority', 'graph_name': 'season', 'region': 'BTH'}
#     return build_ctx(request, ctx, 'graph')


# def init_page_all(request):
#     ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 500, 'time': 'all', 'size': 4, 'centrality': 'authority', 'graph_name': 'all', 'region': 'BTH'}
#     return build_ctx(request, ctx, 'graph')


def init_page_all_10125(request):
    ctx = {'logged': 'true', 'coarse': 'city', 'threshold': 25000, 'time': 'all', 'size': 10, 'centrality': 'authority', 'graph_name': 'all', 'region': 'BTH'}
    return build_ctx2(request, ctx, 'graph')


def init_page_paint_month(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '201910', 'centrality': 'authority', 'graph_name': 'month', 'region': 'BTH'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '2019Q4', 'centrality': 'authority', 'graph_name': 'season', 'region': 'BTH'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_all(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': 'all', 'centrality': 'authority', 'graph_name': 'all', 'region': 'BTH'}
    return build_ctx(request, ctx, 'paint')

