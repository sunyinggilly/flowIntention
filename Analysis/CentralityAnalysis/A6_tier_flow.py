import sys
sys.path.append('/code')
import pandas as pd
import numpy as np
from CONFIG import *
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
from Utils.util_read import read_translation, get_level_dict
from Utils.tools import make_path
plt.switch_backend('agg')


def read_data(timestr):
    df_now = df_graph[df_graph['time'] == timestr]
    df_sum = df_now[['from', 'count']].groupby('from').sum().reset_index()
    dct = {}
    for frm, cnt in df_sum[['from', 'count']].values.tolist():
        dct[frm] = cnt
    df_now['count'] = df_now[['from', 'count']].apply(lambda x: x[1] / dct[x[0]], axis=1)    
    return df_now


if __name__ == "__main__":
    graph_name = 'season'

    # -------------------------- 读centrality数据 -------------------------------
    df_graph = pd.read_csv("%s/%s/graph/city.csv" % (ANA_DATA_PATH, graph_name))
    level_dct = get_level_dict()

    df_graph['from'] = df_graph['from'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_graph['to'] = df_graph['to'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_graph = df_graph[(df_graph['from'] != -1) & (df_graph['to'] != -1)]

    level_lst = ['Tier 1', 'New Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    df_graph['from'] = df_graph['from'].apply(lambda x: level_lst[x])
    df_graph['to'] = df_graph['to'].apply(lambda x: level_lst[x])
    df_graph = df_graph.groupby(['from', 'to', 'time']).sum().reset_index()

    for time_now, time_pre in [['2020Q4', '2019Q4'], ['2020Q1', '2021Q1']]:
        df_now = read_data(time_now)
        df_now.rename(columns={'count': 'now_v'}, inplace=True)
        df_pre = read_data(time_pre)
        df_pre.rename(columns={'count': 'pre_v'}, inplace=True)

        df_now = pd.merge(df_now, df_pre, on=['from', 'to'])
        df_now['Increase'] = df_now[['now_v', 'pre_v']].apply(lambda x: x[0] / x[1] - 1, axis=1)

        df_now['From'] = df_now['from']
        df_now['To'] = df_now['to']
        df_now = df_now.pivot(values='Increase', index='From', columns='To')
        df_now['tier_id'] = df_now.index
        df_now['tier_id'] = df_now['tier_id'].apply(lambda x: level_lst.index(x))
        df_now = df_now.sort_values(by='tier_id')
        df_now = df_now[level_lst]
        sns.heatmap(df_now, center=0, cmap='coolwarm')
        plt.ylabel('From')
        plt.xlabel('To')
        plt.savefig('%s/tier_graph_inc_%s.png' % (OUT_CENTRALITY_PATH, time_now))
        plt.close()
