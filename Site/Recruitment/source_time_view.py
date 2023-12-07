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

data_path = "%s/NTMData/season" % DATA_PATH

df_ftopic_flow = pd.read_csv("%s/out/ftopic_flow.csv" % data_path)
df_ftopic_wtopic = pd.read_csv("%s/out/time_ftopic_wtopic.csv" % data_path)
df_wtopic_word = pd.read_csv("%s/out/wtopic_word.csv" % data_path)
df_city_ftopic = pd.read_csv("%s/out/city_ftopic.csv" % data_path)


def build_paints(vertices_imp, ctx):
    min_w, max_w = 0, 0.1
    nodes = []
    for place_name, w in vertices_imp:  # [北京市, x, y]
        if place_name == '济南市':
            nodes.append({'name': '莱芜市', 'value': min(max_w, round(w, 4))})
        if place_name == '那曲市':
            nodes.append({'name': '那曲地区', 'value': min(max_w, round(w, 4))})
        nodes.append({'name': place_name, 'value': min(max_w, round(w, 4))})

    ctx['min_w'] = min_w
    ctx['max_w'] = max_w
    ctx['color_list'] = ['white', 'yellow', 'orangered', 'red']
    ctx['nodes'] = nodes
    return


def build_ctx(request, ctx):
    # ctx['time_lst'] = df_city_ftopic['time'].drop_duplicates().tolist()
    # ctx['time_lst'].sort()
    ctx['ftopic_lst'] = list(range(df_ftopic_flow['topic'].max() + 1))

    # ------------------------------ 前端输入 -------------------------------------------------------
    if request.POST:
        ctx['topic'] = int(request.POST['Topic'])
        # ctx['time'] = request.POST['Time']

    df_now = df_ftopic_flow[df_ftopic_flow['topic'] == ctx['topic']]
    # df_now = df_now[df_now['time'] == ctx['time']]
    vertices_imp = df_now[['word', 'prob']].values.tolist()
    build_paints(vertices_imp, ctx)
    return render(request, 'source-paint-time.html', ctx)


def init_page(request):
    ctx = {'topic': 0, 'time': '2019Q4'}
    return build_ctx(request, ctx)
