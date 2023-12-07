import sys
sys.path.append('/code')
import pandas as pd
import numpy as np
from CONFIG import *
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
from Utils.util_read import read_translation
plt.switch_backend('agg')

dct_translation = read_translation()

def corr_compare(df_centrality, tar_key, type='pearson', top_K=500):
    df_now = df_centrality[df_centrality[tar_key] != -1]
    df_now = df_now.sort_values(by=tar_key, ascending=False).head(top_K)
    if type == 'pearson':
        cc_mean = df_now[tar_key].mean()
        cc_std = df_now[tar_key].std()
        df_now[tar_key] = df_now[tar_key].apply(lambda x: (x - cc_mean) / cc_std)
    ret = {}

    for centrality in ['pr', 'flow_in', 'flow_out', 'flow_in_net', 'hub', 'authority']:
        if type == 'pearson':
            cc_mean = df_now[centrality].mean()
            cc_std = df_now[centrality].std()
            df_now[centrality] = df_now[centrality].apply(lambda x: (x-cc_mean) / cc_std)
            corr, p = stats.pearsonr(df_now[centrality], df_now[tar_key])
        elif type == 'kendall':
            corr, p = stats.kendalltau(df_now[centrality], df_now[tar_key])
        elif type == 'spearman':
            corr, p = stats.spearmanr(df_now[centrality], df_now[tar_key])
        ret[centrality] = (round(corr, 3), round(p, 5))
    return ret


def read_GDP():
    df = pd.read_csv("%s/GDP/GDP1920.csv" % DATA_PATH).fillna(-1)
    df = df[df['2020Q4'] != -1]
    dct = {}
    for city, gdp in df[['name', '2020Q4']].values.tolist():
        dct[city] = gdp
    return dct


def get_gdp(df_centrality, time_list):
    df = pd.DataFrame()
    for season_str in time_list:
        dct = read_GDP()
        df_now = df_centrality[df_centrality['time'] == season_str]
        df_now['gdp'] = df_now['name'].apply(lambda x: dct[x] if x in dct else -1)
        df = df.append(df_now)
    return df


country_gdp = {'2019Q3': 25104.63, '2019Q4': 27679.80, '2020Q1': 20572.70, 
               '2020Q2': 24898.51, '2020Q3': 26497.63, '2020Q4': 29629.78, '2021Q1': 24931.01}


def cities_appear_in_all_gdp(df, time_list):
    city_set = None
    for timestr in time_list:
        df_now = df[df['time'] == timestr]
        df_now = df_now[df_now['gdp'] != -1]
        cities_now = df_now['name'].drop_duplicates().tolist()
        city_set = set(cities_now) if city_set is None else city_set.intersection(cities_now)
    return city_set


if __name__ == "__main__":
    graph_name = 'all'
    time_list = ['all']
    df_centrality = pd.read_csv("%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name))

    # 取gdp数据
    df_gdp = get_gdp(df_centrality, time_list)
    city_set = cities_appear_in_all_gdp(df_gdp, time_list)

    df_gdp = df_gdp[df_gdp['name'].isin(city_set)]
    for timestr in time_list:
        df_now = df_gdp[df_gdp['time'] == timestr]
        print(corr_compare(df_now, tar_key='gdp'))
        print(corr_compare(df_now, tar_key='gdp', type='spearman'))
