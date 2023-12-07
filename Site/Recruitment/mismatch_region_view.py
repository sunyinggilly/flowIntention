import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
import pandas as pd
from django.shortcuts import render
from CoordGraph import  build_graph
from Functions.read_graph import get_data, df_loc
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
    # elif region_name == 'all':
    #     return  ['广州市', '佛山市', '肇庆市', '深圳市', '东莞市', '惠州市', '珠海市', '中山市', '江门市'] + \
    #             ['北京市', '天津市', '保定市', '廊坊市', '唐山市', '石家庄市', '邯郸市', '秦皇岛市', '张家口市', '承德市', 
    #             '沧州市', '邢台市', '衡水市', '定州市', '辛集市'] + \
    #             ['上海市', '南京市', '无锡市', '常州市', '苏州市', '南通市', '盐城市', '扬州市', '镇江市', '泰州市', '杭州市',
    #             '宁波市', '嘉兴市', '湖州市', '绍兴市', '金华市', '舟山市', '台州市', '合肥市', '芜湖市', '马鞍山市', '铜陵市', '安庆市',
    #             '滁州市', '池州市', '宣城市']

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

def build_paints(cg, vertices, ctx, global_min_w, global_max_w):
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
    ctx['min_w'] = min_w if global_min_w is None else global_min_w
    ctx['max_w'] = max_w if global_max_w is None else global_max_w
    ctx['color_list'] = ['lightblue', 'yellow', 'red']
    ctx['nodes'] = nodes
    return


def build_ctx(request, ctx, type='graph'):
    ctx['region_lst'] = ['YRD', 'BTH', 'PRD']
    ctx['coarse_lst'] = ['city']

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        ctx['time'] = request.POST['Time']
        if type == 'graph':
            ctx['size'] = 4 # float(request.POST['Size'])
            ctx['threshold'] = int(request.POST['Threshold'])
        ctx['centrality'] = request.POST['Centrality']
        ctx['region'] = request.POST['Region']
        if type == 'graph':
            ctx['logged'] = 'true'  # request.POST['Log']

    rcities = get_regions(ctx['region'])
    
    df_graph, _, _, _, _, time_stamps = get_data(coarse='city', graph_name=ctx['graph_name'])
    df_centrality = pd.read_csv("/home/data/suny/works/RFlow/code/ReviewCode/MismatchAnalysis/results/city_%s_mismatch.csv" % ctx['graph_name'])

    centrality_list = list(df_centrality.drop(['name', 'time'], axis=1).columns)
    ctx['centrality_lst'] = centrality_list

    df_centrality_max = df_centrality[centrality_list].max()
    df_centrality_min = df_centrality[centrality_list].min()
    
    df_centrality = df_centrality[df_centrality['name'].isin(rcities)]

    df_graph = df_graph[df_graph['from'].isin(rcities) & df_graph['to'].isin(rcities)]

    ctx['time_lst'] = time_stamps

    cg = get_graph(df_graph, ctx['time'])
    df_centrality = df_centrality[df_centrality['time'] == ctx['time']]

    # 过滤权重
    _, vertices = cg.filter_by_edgeweight(ctx['threshold'])
    # print(vertices)

    # 选择中心度
    set_centrality(cg, df_centrality, centrality=ctx['centrality'])
    global_max = df_centrality_max[ctx['centrality']]
    global_min = df_centrality_min[ctx['centrality']]
    
    build_paints(cg, vertices, ctx, global_min_w=global_min, global_max_w=global_max)
    return render(request, 'centrality-region-paint.html', ctx)


def init_page_paint_month(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '201910', 'centrality': 'edu_mismatch', 'graph_name': 'month', 'region': 'BTH'}
    return build_ctx(request, ctx, 'paint')


def init_page_paint_season(request):
    ctx = {'coarse': 'city', 'threshold': 0, 'time': '2019Q4', 'centrality': 'edu_mismatch', 'graph_name': 'season', 'region': 'BTH'}
    return build_ctx(request, ctx, 'paint')
