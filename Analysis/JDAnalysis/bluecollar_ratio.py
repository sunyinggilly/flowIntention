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


def solve(df, demand_cols):
    level_lst = ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    df['level'] = df['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df = df[df['level'] != -1]
    df = df.drop('name', axis=1).groupby(['level', 'time']).sum().reset_index()
    df_demand = pd.DataFrame()
    for key_col in demand_cols:
        df_now = df[['jd_' + key_col, 'level', 'time']]
        df_demand_sum = df_now[['jd_' + key_col, 'time']].groupby('time').sum().reset_index()
        sum_dct = {}
        for time, count in df_demand_sum[['time', 'jd_' + key_col]].values.tolist():
            sum_dct[time] = count
        df_now['Occupation'] = df_now[['jd_' + key_col, 'time']].apply(lambda x: x[0] / sum_dct[x[1]], axis=1)
        df_now['Demand'] = key_col
        df_now = df_now[['level', 'time', 'Demand', 'Occupation']]
        df_demand = df_demand.append(df_now)


    # 不同级别划分占比 (分别)
    df_demand['Level'] = df_demand['level'].apply(lambda x: level_lst[x])
    df_demand.to_csv("%s/occupation_level/occupation.csv" % OUT_JD_PATH, index=False)

    for demand in demand_cols:
        df_now = df_demand[df_demand['Demand'] == demand]
        df_now['Period'] = df_now['time']
        df_now['Tier'] = df_now['Level']
        sns.lineplot(data=df_now, y='Occupation', x='Period', hue='Tier')
        plt.savefig('%s/%s_ratio.png' % (OUT_JD_PATH, demand))
        plt.close()


if __name__ == "__main__":
    graph_name = 'season'
    time_list = ['2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4', '2021Q1', '2021Q2']

    df_kmeans = pd.read_csv("%s/%s/jd/city_kmeans.csv" % (ANA_DATA_PATH, graph_name))

    level_dct = get_level_dict()
    # solve(df_kmeans, ['Express', 'FactoryWorker', 'PassengerTransport', 'BlueCollar'])
    solve(df_kmeans, ['BlueCollar'])
