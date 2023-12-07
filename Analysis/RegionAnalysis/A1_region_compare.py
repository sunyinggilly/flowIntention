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


def get_regions(region_name='YRD'):
    if region_name == 'PRD':
        return ['广州市', '佛山市', '肇庆市', '深圳市', '东莞市', '惠州市', '珠海市', '中山市', '江门市']
    elif region_name == 'BTH':
        return ['北京市', '天津市', '保定市', '廊坊市', '唐山市', '石家庄市', '邯郸市', '秦皇岛市', '张家口市', '承德市', 
                '沧州市', '邢台市', '衡水市', '定州市', '辛集市']
    elif region_name == 'YRD':
        return ['上海市', '南京市', '无锡市', '常州市', '苏州市', '南通市', '盐城市', '扬州市', '镇江市', '泰州市', '杭州市',
                '宁波市', '嘉兴市', '湖州市', '绍兴市', '金华市', '舟山市', '台州市', '合肥市', '芜湖市', '马鞍山市', '铜陵市', '安庆市',
                '滁州市', '池州市', '宣城']


def build_time_df(df_centrality, key_col, time_list):
    df = None
    for timestr in time_list:
        df_now = df_centrality[df_centrality['time'] == timestr][['name', key_col]]
        df_now = df_now.rename(columns={key_col: timestr}, inplace=False)
        df = df_now if df is None else pd.merge(df, df_now, on='name', how='inner')
    df = df[['name'] + time_list]
    return df


def solve(df, key_col):
    time_list = df['time'].drop_duplicates().sort_values().tolist()
    df_now = build_time_df(df, key_col, time_list)

    df = pd.DataFrame()
    for key in time_list:
        df_tmp = df_now[[key, 'name']]
        df_tmp = df_tmp.rename(columns={key: 'Count (*1000)'}, inplace=False)
        df_tmp['Count (*1000)'] = df_tmp['Count (*1000)'] / 1000
        df_tmp['Period'] = key
        df = df.append(df_tmp)
    df = df.reset_index(drop=True)
    df['Region'] = df['name']
    sns.lineplot(data=df, y='Count (*1000)', x='Period', hue='Region')
    sns.scatterplot(data=df, hue='Region', y='Count (*1000)', x='Period', s=50, legend=False)
    plt.xticks(rotation=30)

    plt.savefig('%s/%s/%s_change_region_compare.png' % (OUT_REGION_PATH, graph_name, key_col))
    plt.close()


def occupation_solve(df, key_cols, base_col, graph_name):
    df_demand = pd.DataFrame()
    for key_col in key_cols:
        df_now = df[['jd_' + key_col, 'jd_' + base_col, 'name', 'time']]
        df_now['Occupation'] = df_now[['jd_' + key_col, 'jd_' + base_col]].apply(lambda x: x[0] / x[1], axis=1)
        df_now['Demand'] = key_col
        df_now = df_now[['name', 'time', 'Demand', 'Occupation']]
        df_demand = df_demand.append(df_now)
    df_demand = df_demand.reset_index(drop=True)
    for city in df['name'].drop_duplicates().tolist():
        df_now = df_demand[df_demand['name'] == city]
        df_now['Period'] = df_now['time']
        lineplt = sns.lineplot(data=df_now, y='Occupation', x='Period', hue='Demand')
        sns.scatterplot(data=df_now, hue='Demand', y='Occupation', x='Period', s=50, legend=False)
        plt.xticks(rotation=30)
        lineplt.legend(loc='best', ncol=2, fancybox=True)

        plt.savefig('%s/occupation/%s/line_%s_%s.png' % (OUT_REGION_PATH, graph_name, city, base_col))
        plt.close()

if __name__ == "__main__":
    region_dct = {'BTH': get_regions('BTH'), 'PRD': get_regions('PRD'), 'YRD': get_regions('YRD')}
    cities = []
    city2region = {}
    for region, region_cities in region_dct.items():
        cities.extend(region_cities)
        for city in region_cities:
            city2region[city] = region

    for graph_name in ['season', 'month']:
        make_path('%s/occupation/%s/' % (OUT_REGION_PATH, graph_name))
        make_path('%s/%s/' % (OUT_REGION_PATH, graph_name))

        df_centrality = pd.read_csv("%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name))
        df_kmeans = pd.read_csv("%s/%s/jd/city_kmeans.csv" % (ANA_DATA_PATH, graph_name))
        df_kmeans.rename(columns={'jd_FactoryWorker':'jd_Manufacturing'}, inplace=True)
        df_centrality = pd.merge(df_centrality, df_kmeans, on=['name', 'time'], how='left').fillna(0)
        df_centrality = df_centrality[df_centrality['name'].isin(cities)]
        df_centrality['name'] = df_centrality['name'].apply(lambda x: city2region[x])
        df_centrality = df_centrality.groupby(['name', 'time']).sum().reset_index()
        if graph_name == 'season':
            df_centrality = df_centrality[df_centrality['time']<='2021Q4']
        else:
            df_centrality = df_centrality[df_centrality['time']<=202112]
            df_centrality['time'] = pd.to_datetime(df_centrality['time'].astype(str), format='%Y%m')

        solve(df_centrality, 'jd_Blue Collar')
        solve(df_centrality, 'jd_White Collar')

        # if graph_name == 'season':        
        solve(df_centrality, 'jd_Transporter')
        solve(df_centrality, 'jd_Factory Worker')
        occupation_solve(df_centrality, ['Transporter', 'Factory Worker', 'Public Transit Staff'], 'Blue Collar', graph_name)
