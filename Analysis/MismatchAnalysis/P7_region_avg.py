import sys
sys.path.append('/code')

from CONFIG import *
from Utils.util_read import read_graph_from_file
from Utils.util_read import read_translation, get_level_dict
from Utils.tools import make_path
import pandas as pd
import seaborn as sns
import math
import matplotlib.pyplot as plt
plt.switch_backend('agg')

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

def get_ratio_column(df):
    df_all = df[['time', 'name', 'count']].groupby(['time', 'name']).sum().reset_index()
    df_all.rename(columns={'count': 'all'}, inplace=True)
    df = pd.merge(df, df_all, on=['time', 'name']) # [time, city, type, count, all]
    df['ratio'] = df['count'] / df['all']
    return df.drop('all', axis=1)

def get_rank_column(df, score_col):

    def rank_scores(group):
        group['rank'] = group[score_col].rank(method='average', ascending=False) 
        return group

    df = df.groupby(['time', 'name'], group_keys=False).apply(rank_scores)
    return df


if __name__ == "__main__":
    mode = 'industry'
    region_dct = {'BTH': get_regions('BTH'), 'PRD': get_regions('PRD'), 'YRD': get_regions('YRD')}
    cities = []
    city2region = {}
    for region, region_cities in region_dct.items():
        cities.extend(region_cities)
        for city in region_cities:
            city2region[city] = region

    for graph_name in ['season']:
        df_all = None
        for mode in ['industry']:
            df_demand = pd.read_csv('{}/{}/jd_{}.csv'.format(OUT_MISMATCH_PATH, mode, graph_name)) # 分行业的
            df_supply = pd.read_csv('{}/{}/centrality/{}/{}.csv'.format(OUT_MISMATCH_PATH, mode, 'city', graph_name)) [['time', 'name', 'value', 'flow_in_net_country_norm']]
            df_supply.rename(columns={'value': 'type'}, inplace=True)

            if graph_name == 'season':
                df_supply = df_supply[df_supply['time'] >= '2019Q4']
                df_demand = df_demand[df_demand['time'] >= '2019Q4']
            else:
                df_demand['time'] = df_demand['time'].apply(lambda x: '%d%02d' % (int(x.split('-')[0]), int(x.split('-')[1])))
                df_demand = df_demand[df_demand['time'] >= '201910']
                df_supply['time'] = df_supply['time'].apply(lambda x: '%d%02d' % (int(x.split('-')[0]), int(x.split('-')[1])))
                df_supply = df_supply[df_supply['time'] >= '201910']

            df_demand = df_demand[['time', 'city', 'type', 'count']].groupby(['time', 'city', 'type']).sum().reset_index()
            df_demand.rename(columns={'city': 'name'}, inplace=True)
            df_supply = df_supply[['time', 'name', 'type', 'flow_in_net_country_norm']].groupby(['time', 'name', 'type']).sum().reset_index()

            df_demand = get_ratio_column(df_demand)
            df_demand = df_demand[df_demand['type']!='其他']
            df_demand = get_rank_column(df_demand, score_col='ratio').sort_values(by=['time', 'name', 'rank'])
            df_supply = get_rank_column(df_supply, score_col='flow_in_net_country_norm').sort_values(by=['time', 'name', 'rank'])
            df_supply = df_supply[df_supply['type']!='其他']
            
            df = pd.merge(df_demand, df_supply, on=['time', 'name', 'type'], suffixes=['_demand', '_supply']).drop('type', axis=1)
            df_demand_top10 = df[df['rank_demand'] <= 10]
            df_supply_top10 = df[df['rank_supply'] <= 10]

            df['{}_mismatch'.format(mode)] = (df['rank_demand'] - df['rank_supply']).apply(lambda x: math.fabs(x))
            df['{}_demand_lack'.format(mode)] = (df['rank_demand'] - df['rank_supply']).apply(lambda x: max(x, 0))
            df['{}_supply_lack'.format(mode)] = (df['rank_supply'] - df['rank_demand']).apply(lambda x: max(x, 0))
            df = df.groupby(['time', 'name']).mean().reset_index()
            df = df[['time', 'name', '{}_mismatch'.format(mode), '{}_demand_lack'.format(mode), '{}_supply_lack'.format(mode)]]

            df_demand_top10['{}_mismatch_dtop10'.format(mode)] = (df_demand_top10['rank_demand'] - df_demand_top10['rank_supply']).apply(lambda x: math.fabs(x))
            df_demand_top10['{}_demand_lack_dtop10'.format(mode)] = (df_demand_top10['rank_demand'] - df_demand_top10['rank_supply']).apply(lambda x: max(x, 0))
            df_demand_top10['{}_supply_lack_dtop10'.format(mode)] = (df_demand_top10['rank_supply'] - df_demand_top10['rank_demand']).apply(lambda x: max(x, 0))
            df_demand_top10 = df_demand_top10.groupby(['time', 'name']).mean().reset_index()
            df_demand_top10 = df_demand_top10[['time', 'name', '{}_mismatch_dtop10'.format(mode), '{}_demand_lack_dtop10'.format(mode), '{}_supply_lack_dtop10'.format(mode)]]

            df_supply_top10['{}_mismatch_stop10'.format(mode)] = (df_supply_top10['rank_demand'] - df_supply_top10['rank_supply']).apply(lambda x: math.fabs(x))
            df_supply_top10['{}_demand_lack_stop10'.format(mode)] = (df_supply_top10['rank_demand'] - df_supply_top10['rank_supply']).apply(lambda x: max(x, 0))
            df_supply_top10['{}_supply_lack_stop10'.format(mode)] = (df_supply_top10['rank_supply'] - df_supply_top10['rank_demand']).apply(lambda x: max(x, 0))
            
            df_supply_top10 = df_supply_top10.groupby(['time', 'name']).mean().reset_index()
            df_supply_top10 = df_supply_top10[['time', 'name', '{}_mismatch_stop10'.format(mode), '{}_demand_lack_stop10'.format(mode), '{}_supply_lack_stop10'.format(mode)]]

            df = df.merge(df_demand_top10, on=['time', 'name'], how='outer')
            df = df.merge(df_supply_top10, on=['time', 'name'], how='outer')

            if df_all is None:
                df_all = df
            else:
                df_all = df_all.merge(df, on=['time', 'name'], how='outer')

        df_all = df_all[df_all['name'].isin(cities)]
        df_all['region'] = df_all['name'].apply(lambda x: city2region[x])
        df_all = df_all.drop('name', axis=1)
        df_all = df_all.groupby(['time', 'region']).mean().reset_index()
        print(df_all[['time', 'region', 'industry_mismatch']])
        