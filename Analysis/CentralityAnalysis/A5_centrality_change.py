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


dct_translation = read_translation()


def get_rank(df_c, centrality, time):
    df = df_c[df_c['time'] == time]
    df = df[['name', centrality]]
    df = df.sort_values(by=centrality, ascending=False).head(100)
    df['rank'] = [i + 1 for i in range(df.shape[0])]
    df[centrality] = df[centrality].apply(lambda x: round(x, 4))
    df_now = df[['name', centrality]]
    df_now['name'] = df_now['name'].apply(lambda x: dct_translation[x])
    df_now.rename(columns={'name': 'name_%s' % time, centrality: '%s_%s' % (centrality, time)}, inplace=True)
    return df_now.reset_index(drop=True)


def build_time_df(df_centrality, key_col, time_list):
    df = None
    for timestr in time_list:
        df_now = df_centrality[df_centrality['time'] == timestr][['name', key_col]]
        df_now = df_now.rename(columns={key_col: timestr}, inplace=False)
        df = df_now if df is None else pd.merge(df, df_now, on='name', how='inner')
    df = df[['name'] + time_list]
    return df


def solve(df, key_col):
    df_now = build_time_df(df, key_col, ['2019Q4', '2020Q1', '2020Q2', '2020Q4', '2021Q1', '2021Q2'])
    df_now['level'] = df_now['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_now = df_now[df_now['level'] != -1]
    
    df_now['Q4'] = df_now[['2020Q4', '2019Q4']].apply(lambda x: (x[0] - x[1]) / x[1], axis=1)
    df_now['Q1'] = df_now[['2020Q1', '2021Q1']].apply(lambda x: (x[0] - x[1]) / x[1], axis=1)
    df_now['Q2'] = df_now[['2020Q2', '2021Q2']].apply(lambda x: (x[0] - x[1]) / x[1], axis=1)

    df_now['19Q4Q1I'] = df_now[['2019Q4', '2020Q1']].apply(lambda x: (x[0] - x[1]) / x[1], axis=1)
    df_now['20Q4Q1I'] = df_now[['2020Q4', '2021Q1']].apply(lambda x: (x[0] - x[1]) / x[1], axis=1)
    df_now['Q4Q1II'] = df_now[['19Q4Q1I', '20Q4Q1I']].apply(lambda x: (x[0] - x[1]) / x[1], axis=1)

    level_lst = ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    df = pd.DataFrame()    
    for key in ['Q4', 'Q1', 'Q2']:
        df_tmp = df_now[[key, 'level']]
        df_tmp = df_tmp.rename(columns={key: 'increase'}, inplace=False)
        df_tmp['metric'] = key
        df = df.append(df_tmp)
    df.to_csv("%s/%s_change_cities.csv" % (OUT_CENTRALITY_PATH, key_col), index=False)
    df['Period'] = df['metric']
    df['Tier'] = df['level'].apply(lambda x: level_lst[x])
    df['Increase'] = df['increase']
    sns.boxplot(data=df[df['metric'] != 'Q4Q1II'], y='Increase', x='Period', hue='Tier', hue_order=level_lst, showfliers=False)
    plt.savefig('%s/level_boxplot_%s.png' % (OUT_CENTRALITY_PATH, key_col))
    plt.close()


if __name__ == "__main__":
    graph_name = 'season'

    df_centrality = pd.read_csv("%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name))

    df_centrality['ratio'] = df_centrality[['hub', 'authority']].apply(lambda x: (x[0] + 1e-9) / (x[1] + 1e-9), axis=1)
    level_dct = get_level_dict()

    solve(df_centrality, 'authority')
    solve(df_centrality, 'hub')
