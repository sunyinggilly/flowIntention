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
    timelist = df['time'].drop_duplicates().sort_values().tolist()
    df_now = build_time_df(df, key_col, timelist)
    df_now['level'] = df_now['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_now = df_now[df_now['level'] != -1]
    df_now = df_now.drop('name', axis=1).groupby('level').sum().reset_index()

    df = pd.DataFrame()
    for key in timelist:
        df_tmp = df_now[[key, 'level']]
        df_tmp = df_tmp.rename(columns={key: 'Count (*1000)'}, inplace=False)
        df_tmp['metric'] = key
        df = df.append(df_tmp)

    level_lst = ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    df = df.reset_index(drop=True)
    df['Period'] = df['metric']
    df['Tier'] = df['level'].apply(lambda x: level_lst[x])
    df['Count (*1000)'] = df['Count (*1000)'] / 1000
    lineplt = sns.lineplot(data=df, y='Count (*1000)', x='Period', hue='Tier')
    sns.scatterplot(data=df, hue='Tier', y='Count (*1000)', x='Period', s=50, legend=False)
    lineplt.legend(loc='best', ncol=3, fancybox=True)
    plt.xticks(rotation=30) 
    plt.savefig('%s/level_lineplot_%s_%s.png' % (OUT_JD_PATH, graph_name, key_col))
    plt.close()


if __name__ == "__main__":
    make_path(OUT_JD_PATH)
    for graph_name in ['season', 'month']:
        df_centrality = pd.read_csv("%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name))
        df_kmeans = pd.read_csv("%s/%s/jd/city_kmeans.csv" % (ANA_DATA_PATH, graph_name))
        df_centrality = pd.merge(df_centrality, df_kmeans, on=['name', 'time'], how='left').fillna(0)
        if graph_name == 'season':
            df_centrality = df_centrality[df_centrality['time']<='2021Q4']
        
        if graph_name == 'month':
            df_centrality = df_centrality[df_centrality['time']<=202112]
            df_centrality['time'] = pd.to_datetime(df_centrality['time'].astype(str), format='%Y%m')

        df_centrality['ratio'] = df_centrality[['hub', 'authority']].apply(lambda x: (x[0] + 1e-9) / (x[1] + 1e-9), axis=1)
        level_dct = get_level_dict()

        solve(df_centrality, 'jd_Blue Collar')
        solve(df_centrality, 'jd_White Collar')
        solve(df_centrality, 'jd_Transporter')
        solve(df_centrality, 'jd_Engineer')
        solve(df_centrality, 'jd_Designer')
        solve(df_centrality, 'jd_Public Transit Staff')
        solve(df_centrality, 'jd_Factory Worker')
        solve(df_centrality, 'jd_Manager')