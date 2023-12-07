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

def level_boxplot(df_centrality, key, time_list):
    df_centrality = df_centrality[(df_centrality['time'].isin(time_list))]
    level_lst = ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    df_centrality['Tier'] = df_centrality['Tier'].apply(lambda x: level_lst[x])
    df_centrality[key.capitalize()] = df_centrality[key]
    sns.boxplot(data=df_centrality, y=key.capitalize(), x='Tier', hue='time', order=level_lst)
    plt.savefig('%s/level_boxplot_%s_%sto%s.png' % (OUT_CENTRALITY_PATH, key, time_list[0], time_list[-1]))
    plt.close()

if __name__ == "__main__":
    sum_cols = ['authority', 'hub']
    mean_cols = ['gross_flow', 'flow_in_net_country_norm']
    out_path = '%s/temporal_centrality' % OUT_CENTRALITY_PATH
    make_path(out_path)
    for graph_name in ['season', 'month']:
        centrality_path = "%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name)

        # -------------------------- 读centrality数据 -------------------------------
        df_centrality = pd.read_csv(centrality_path)
        
        level_dct = get_level_dict()
        df_centrality['Tier'] = df_centrality['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
        df_centrality = df_centrality[['time', 'name', 'Tier'] + sum_cols + mean_cols]
        df_centrality = df_centrality[df_centrality['Tier'] != -1]
        df_centrality = df_centrality.sort_values(by='time')

        if graph_name == 'season':
            for key_col in sum_cols + mean_cols:
                level_boxplot(df_centrality, key=key_col, time_list=['2019Q4', '2020Q4', '2021Q4', '2022Q4'])

        level_lst =  ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
        
        df_level = df_centrality[['time', 'Tier'] + sum_cols].groupby(['time', 'Tier']).sum().reset_index()
        df_level_mean = df_centrality[['time', 'Tier'] + mean_cols].groupby(['time', 'Tier']).mean().reset_index()
        df_level = pd.merge(df_level, df_level_mean, on=['time', 'Tier'])

        map_dct = {'gross_flow': 'Gross Flow', 'flow_in_net_country_norm': 'Net Inflow(‰)'}
        df_level = df_level.rename(columns={'time': 'Period'})

        if graph_name == 'month':
            df_level['Period'] = pd.to_datetime(df_level['Period'].astype(str), format='%Y%m') 

        for key_col in sum_cols + mean_cols:
            df_now = df_level[['Period', 'Tier', key_col]]
            df_now['Tier'] = df_now['Tier'].apply(lambda x: level_lst[x])
            if key_col in map_dct.keys():
                df_now.rename(columns={key_col: map_dct[key_col]}, inplace=True)
                key_col = map_dct[key_col]
            else:
                df_now.rename(columns={key_col: key_col.capitalize()}, inplace=True)
                key_col = key_col.capitalize()
            
            lineplt = sns.lineplot(data=df_now, hue='Tier', y=key_col, x='Period', ci=95)
            sns.scatterplot(data=df_now, hue='Tier', y=key_col, x='Period', s=50, legend=False)
            plt.xticks(rotation=30)

            lineplt.legend(loc='best', ncol=3, fancybox=True)

            plt.savefig('%s/%s_%s.png' % (out_path, key_col, graph_name))
            plt.close()
            
            df_tmp = df_now[~df_now['Tier'].isin(['Tier 1', 'New tier 1'])]
            lineplt = sns.lineplot(data=df_tmp, hue='Tier', y=key_col, x='Period', ci=95)
            sns.scatterplot(data=df_tmp, hue='Tier', y=key_col, x='Period', s=50, legend=False)
            plt.xticks(rotation=30) 
            
            lineplt.legend(loc='best', ncol=4, fancybox=True)

            plt.savefig('%s/%s_%s_t2.png' % (out_path, key_col, graph_name))
            plt.close()
            
            df_tmp = df_now[df_now['Tier'].isin(['Tier 1', 'New tier 1'])]
            lineplt = sns.lineplot(data=df_tmp, hue='Tier', y=key_col, x='Period', ci=95)
            sns.scatterplot(data=df_tmp, hue='Tier', y=key_col, x='Period', s=50, legend=False)
            plt.xticks(rotation=30) 
            
            lineplt.legend(loc='best', ncol=3, fancybox=True)

            plt.savefig('%s/%s_%s_t1.png' % (out_path, key_col, graph_name))
            plt.close()