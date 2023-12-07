import sys
sys.path.append('/code')
import pandas as pd
import numpy as np
from CONFIG import *
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
from Utils.util_read import read_translation, get_level_dict
plt.switch_backend('agg')


dct_translation = read_translation()


def solve(df, key_cols, base_col):
    df['level'] = df['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df = df[df['level'] != -1]
    df = df.drop('name', axis=1).groupby(['level', 'time']).sum().reset_index()
    df_demand = pd.DataFrame()
    for key_col in key_cols:
        df_now = df[['jd_' + key_col, 'jd_' + base_col, 'level', 'time']]
        df_now['Occupation'] = df_now[['jd_' + key_col, 'jd_' + base_col]].apply(lambda x: x[0] / x[1], axis=1)
        df_now['Demand'] = key_col
        df_now = df_now[['level', 'time', 'Demand', 'Occupation']]
        df_demand = df_demand.append(df_now)
    # df_demand.to_csv("%s/occupation/%s.csv" % (OUT_JD_PATH, base_col), index=False)
    df_demand = df_demand.reset_index(drop=True)
    for level in df['level'].drop_duplicates().tolist():
        df_now = df_demand[df_demand['level'] == level]
        df_now['Level'] = df_now['level'].apply(lambda x: 'l%d' % x)
        df_now['Period'] = df_now['time']
        sns.lineplot(data=df_now, y='Occupation', x='Period', hue='Demand')
        plt.savefig('%s/occupation/line_l%d_%s.png' % (OUT_JD_PATH, level, base_col))
        plt.close()


def solve_wholecountry(df, key_cols, base_col):
    df['level'] = 0
    df = df[df['level'] != -1]
    df = df.drop('name', axis=1).groupby(['level', 'time']).sum().reset_index()
    df_demand = pd.DataFrame()
    for key_col in key_cols:
        df_now = df[['jd_' + key_col, 'jd_' + base_col, 'level', 'time']]
        df_now['Occupation'] = df_now[['jd_' + key_col, 'jd_' + base_col]].apply(lambda x: x[0] / x[1], axis=1)
        df_now['Demand'] = key_col
        df_now = df_now[['level', 'time', 'Demand', 'Occupation']]
        df_demand = df_demand.append(df_now)
    # df_demand.to_csv("%s/occupation/whole_%s_%s.csv" % (OUT_JD_PATH, key_col, base_col), index=False)
    df_demand = df_demand.reset_index(drop=False)
    for level in df['level'].drop_duplicates().tolist():
        df_now = df_demand[df_demand['level'] == level]
        df_now['Level'] = df_now['level'].apply(lambda x: 'l%d' % x)
        df_now['Period'] = df_now['time']
        sns.lineplot(data=df_now, y='Occupation', x='Period', hue='Demand')
        plt.savefig('%s/occupation/line_whole_%s.png' % (OUT_JD_PATH, base_col))
        plt.close()


if __name__ == "__main__":
    graph_name = 'season'
    time_list = ['2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4', '2021Q1', '2021Q2']

    df_kmeans = pd.read_csv("%s/%s/jd/city_kmeans.csv" % (ANA_DATA_PATH, graph_name))
    df_kmeans.rename(columns={'jd_FactoryWorker':'jd_Manufacturing'}, inplace=True)
        
    level_dct = get_level_dict()
    solve(df_kmeans, ['Express', 'Manufacturing', 'PassengerTransport'], 'BlueCollar')
    solve_wholecountry(df_kmeans, ['Express', 'Manufacturing', 'PassengerTransport'], 'BlueCollar')
