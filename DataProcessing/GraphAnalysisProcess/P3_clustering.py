import sys
sys.path.append('/code')
import pandas as pd
from CONFIG import *
from tqdm import tqdm
from Utils.util_read import read_graph_from_file, read_location
from CoordGraph import build_graph
from Utils.tools import make_path


def solve(df_graph, df_loc):
    time_lst = df_graph['time'].drop_duplicates().tolist()
    df = pd.DataFrame()
    df_previous = None
    for timestr in tqdm(time_lst):        
        df_tmp = df_graph[df_graph['time'] == timestr][['from', 'to', 'count']]
        cg = build_graph(df_tmp, df_loc, places=None)
        df_now = pd.DataFrame()
        df_now['name'] = cg.places
        df_now['time'] = timestr
        for res in [0.5, 0.8, 1]:
            dct_init = {}
            if df_previous is not None:
                for u, clsid in enumerate(df_previous['louvain_%.2f' % res].tolist()):
                    dct_init[u] = clsid
            df_now['louvain_%.2f' % res] = cg.calc_cluster_lovain(normalize=False, resolution=res, init_cls=dct_init)
            dct_init = {}
            if df_previous is not None:
                for u, clsid in enumerate(df_previous['louvain_%.2f_norm' % res].tolist()):
                    dct_init[u] = clsid
            df_now['louvain_%.2f_norm' % res] = cg.calc_cluster_lovain(normalize=True, resolution=res, init_cls=dct_init)
        df = df.append(df_now)
        df_previous = df_now
    df = color_adjust(df)
    return df


def color_adjust(df_cls):
    res_lst = [0.5, 0.8, 1]
    time_lst = df_cls['time'].drop_duplicates().tolist()
    df = pd.DataFrame()
    dct_count = {}
    for timestr in tqdm(time_lst):
        df_now = df_cls[df_cls['time'] == timestr]
        for res in res_lst:
            for cls_name in ['louvain_%.2f' % res, 'louvain_%.2f_norm' % res]:
                dct_ret = {}
                if cls_name != 'louvain_%.2f' % res_lst[0]:
                    vis_cls_now = [0] * 50
                    vis_cls_pre = [0] * 50

                    # 数对应关系
                    cls_tar = [[0] * 50 for i in range(50)]                    
                    for city, clsid in df_now[['name', cls_name]].values.tolist():
                        for i in range(50):
                            cls_tar[clsid][i] += dct_count[city][i]
                    
                    cls_tar = [[(u, count) for u, count in enumerate(cls_count)] for cls_count in cls_tar]                    
                    
                    records = []
                    # 对应到最多的那个
                    for u, cls_count in enumerate(cls_tar):
                        cls_count.sort(key=lambda x: x[1], reverse=True)
                        if cls_count[0] == 0:
                            break
                        for pre_cls, cc in cls_count:
                            records.append([u, pre_cls, cc])
                    records.sort(key=lambda x: x[2], reverse=True)
                    for u, pre_cls, _ in records:
                        if vis_cls_now[u] == 0 and vis_cls_pre[pre_cls] == 0:
                            vis_cls_now[u] = 1
                            vis_cls_pre[pre_cls] = 1
                            dct_ret[u] = pre_cls

                    df_now[cls_name] = df_now[cls_name].apply(lambda x: dct_ret[x])

                for name, clsid in df_now[['name', cls_name]].values.tolist():
                    if name not in dct_count:
                        dct_count[name] = [0] * 50
                    dct_count[name][clsid] += 1
        
        df = df.append(df_now)
    return df

if __name__ == "__main__":
    for GRAPH_NAME in ['all', 'season', 'month']:
        make_path("%s/%s/clustering/" % (ANA_DATA_PATH, GRAPH_NAME))
        df_loc_mc = read_location(coord_sys='mc', coarse='km')
        df_loc_ll = read_location(coord_sys='ll', coarse=None)
        df_loc = pd.merge(df_loc_mc, df_loc_ll, on=['name'])[['name', 'll_x', 'll_y', 'mc_x', 'mc_y']]

        df_province = read_graph_from_file(coarse='province', self_edge=False, graph_name=GRAPH_NAME)
        df_cluster_province = solve(df_province, df_loc)
        df_cluster_province.to_csv("%s/%s/clustering/province_cluster.csv" % (ANA_DATA_PATH, GRAPH_NAME), index=False)

        df_city = read_graph_from_file(coarse='city', self_edge=False, graph_name=GRAPH_NAME)
        df_cluster_city = solve(df_city, df_loc)
        df_cluster_city.to_csv("%s/%s/clustering/city_cluster.csv" % (ANA_DATA_PATH, GRAPH_NAME), index=False)
