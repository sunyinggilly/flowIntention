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


def value_plot(df_centrality, filename='auth_hub_classify', text_x_bottom=0, text_y_bottom=0):
    color_lst = ['#5767C9', '#7BD575', '#FFC849', '#FF4D5D', '#5FC2E1', '#00AA73']
    for i in range(6):
        df_now = df_centrality[df_centrality['level'] == i]
        plt.plot(df_now['authority'].tolist(), df_now['hub'].tolist(), "o", c=color_lst[i], linewidth=2)

    plt.xlabel('Authority')
    plt.ylabel('Hub')
    auth_med = df_centrality['authority'].median()
    hub_med = df_centrality['hub'].median()
    plt.plot([auth_med, auth_med], [0, df_centrality['hub'].max()], 'g-', linewidth=2)
    plt.plot([0, df_centrality['authority'].max()], [hub_med, hub_med], 'g-', linewidth=2)
    if filename.split('_')[-1] == 'all':
        lst = ['Dongguan', 'Suzhou', 'Guangzhou', 'Beijing', 'Shenzhen', 'Shanghai', 'Xiamen', 'Hangzhou', 'Ningbo', 
               'Huizhou', 'Fuzhou', 'Taiyuan', 'Kunming', 'Langfang', 'Changchun', 'Harbin', 'Xiamen', 'Qingdao', 
               'Changsha', 'Shenyang', 'Shaoxing', 'Yancheng', 'Xinyang', 'Zhuhai', 'Weifang', 'Ganzhou', 'Shantou', 
               'Luoyang', 'Tangshan'] # 'Lanzhou', 'Guiyang',
    else:    
        lst = ['Dongguan', 'Suzhou', 'Guangzhou', 'Beijing', 'Shenzhen', 'Shanghai', 'Xiamen', 'Hangzhou', 'Wuxi', 'Ningbo', 
               'Huizhou', 'Fuzhou', 'Taiyuan', 'Kunming', 'Xi\'an', 'Langfang', 'Changchun', 'Harbin', 'Xiamen', 'Qingdao', 
               'Changsha', 'Hefei', 'Shenyang', 'Shaoxing', 'Yancheng', 'Xinyang', 'Zhuhai', 'Weifang', 'Ganzhou', 'Shantou', 
               'Luoyang', 'Tangshan']  # 'Lanzhou', 'Guiyang',
    for name, x, y in df_centrality[['name', 'authority', 'hub']].values.tolist():
        if x < text_x_bottom and y < text_y_bottom:
            continue
        if dct_translation[name] in lst and not (dct_translation[name] == 'Suzhou' and filename.split('_')[-2] == '3'):
            if dct_translation[name] == 'Ningbo':
                plt.text(x - 0.002, y + 0.001, dct_translation[name], color="b", fontsize=12)
            else:
                plt.text(x - 0.002, y + 0.0007, dct_translation[name], color="b", fontsize=12)

    plt.savefig('%s/wholeyear/auth_hub_2D.png' % OUT_CENTRALITY_PATH)
    plt.close()


def level_boxplot(df_centrality, key, time_list):
    df_centrality = df_centrality[(df_centrality['time'].isin(time_list))]
    level_lst = ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    df_centrality['Tier'] = df_centrality['level'].apply(lambda x: level_lst[x])
    df_centrality[key.capitalize()] = df_centrality[key]
    sns.boxplot(data=df_centrality, y=key.capitalize(), x='Tier', order=level_lst)
    plt.savefig('%s/wholeyear/level_boxplot_%s.png' % (OUT_CENTRALITY_PATH, key))
    plt.close()


def hub_auth_2d(df_centrality, time_list):
    for timestr in time_list:
        df_time = df_centrality[df_centrality['time'] == timestr]
        for level in range(6):
            df_now = df_time[(df_time['level'] == level)]
            value_plot(df_now, filename='auth_hub_classify_%d_%s' % (level, timestr))    
        value_plot(df_time, filename='auth_hub_classify_%s' % timestr, text_x_bottom=0.009, text_y_bottom=0.01)


if __name__ == "__main__":
    graph_name = 'all'
    make_path('%s/wholeyear/' % OUT_CENTRALITY_PATH)
    
    # -------------------------- 读centrality数据 -------------------------------
    df_centrality = pd.read_csv("%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name))

    level_dct = get_level_dict()
    df_centrality['level'] = df_centrality['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_centrality = df_centrality[['time', 'name', 'authority', 'hub', 'level']]
    df_centrality = df_centrality[df_centrality['level'] != -1]
    df_centrality = df_centrality.sort_values(by='time')
    
    # --------------------------- ratio -----------------------------------------
    df_centrality['ratio'] = df_centrality[['hub', 'authority']].apply(lambda x: (x[0] + 1e-9) / (x[1] + 1e-9), axis=1)
    level_boxplot(df_centrality, key='ratio', time_list=['all'])

    # ---------------------------- 不同级别城市auth, hub分布 2D图 ------------------------
    hub_auth_2d(df_centrality, ['all'])
