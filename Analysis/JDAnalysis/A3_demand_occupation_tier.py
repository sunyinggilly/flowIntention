import sys
sys.path.append('/code')
import pandas as pd
import numpy as np
from CONFIG import *
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
from Utils.tools import make_path
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
    df_demand = df_demand.reset_index(drop=True)
    for level in df['level'].drop_duplicates().tolist():
        df_now = df_demand[df_demand['level'] == level]
        df_now['Level'] = df_now['level'].apply(lambda x: 'l%d' % x)
        df_now['Period'] = df_now['time']
        sns.lineplot(data=df_now, y='Occupation', x='Period', hue='Demand')
        sns.scatterplot(data=df_now, hue='Demand', y='Occupation', x='Period', s=50, legend=False)
        plt.xticks(rotation=30) 
        plt.savefig('%s/occupation/%s/line_l%d_%s.png' % (OUT_JD_PATH, graph_name, level, base_col))
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
    df_demand = df_demand.reset_index(drop=False)
    for level in df['level'].drop_duplicates().tolist():
        df_now = df_demand[df_demand['level'] == level]
        df_now['Level'] = df_now['level'].apply(lambda x: 'l%d' % x)
        df_now['Period'] = df_now['time']
        lineplt = sns.lineplot(data=df_now, y='Occupation', x='Period', hue='Demand')
        sns.scatterplot(data=df_now, hue='Demand', y='Occupation', x='Period', s=50, legend=False)
        plt.xticks(rotation=30) 
        plt.savefig('%s/occupation/%s/line_whole_%s.png' % (OUT_JD_PATH, graph_name, base_col))
        plt.close()


if __name__ == "__main__":

    for graph_name in ['season', 'month']:
        make_path('%s/occupation/%s/' % (OUT_JD_PATH, graph_name))
        df_kmeans = pd.read_csv("%s/%s/jd/city_kmeans.csv" % (ANA_DATA_PATH, graph_name))
        df_kmeans.rename(columns={'jd_FactoryWorker':'jd_Manufacturing'}, inplace=True)

        if graph_name == 'month':
            df_kmeans['time'] = pd.to_datetime(df_kmeans['time'].astype(str), format='%Y%m')
            
        level_dct = get_level_dict()
        solve(df_kmeans, ['Transporter', 'Factory Worker', 'Public Transit Staff'], 'Blue Collar')
        solve_wholecountry(df_kmeans, ['Transporter', 'Factory Worker', 'Public Transit Staff'], 'Blue Collar')
