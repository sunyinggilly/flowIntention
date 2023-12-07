import sys
sys.path.append('/code')
from CONFIG import *
import pandas as pd
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
    df_all = df[['time', 'region', 'count']].groupby(['time', 'region']).sum().reset_index()
    df_all.rename(columns={'count': 'all'}, inplace=True)
    df = pd.merge(df, df_all, on=['time', 'region']) 
    df['ratio'] = df['count'] / df['all']
    return df.drop('all', axis=1)

def get_rank_column(df, score_col):

    def rank_scores(group):
        group['rank'] = group[score_col].rank(method='average', ascending=False) 
        return group

    df = df.groupby(['time', 'region'], group_keys=False).apply(rank_scores)
    return df


if __name__ == "__main__":
    region_dct = {'BTH': get_regions('BTH'), 'PRD': get_regions('PRD'), 'YRD': get_regions('YRD')}
    cities = []
    city2region = {}
    for region, region_cities in region_dct.items():
        cities.extend(region_cities)
        for city in region_cities:
            city2region[city] = region
    for mode in ['industry']:
        for graph_name in ['season']:
            df_demand = pd.read_csv('{}/{}/jd_{}.csv'.format(OUT_MISMATCH_PATH, mode, graph_name)) 

            df_supply = pd.read_csv('{}/{}/centrality/{}/{}.csv'.format(OUT_MISMATCH_PATH, mode, 'city', graph_name)) [['time', 'name', 'value', 'flow_in_net_country_norm']]
            df_supply.rename(columns={'value': 'type'}, inplace=True)

            df_supply = df_supply[df_supply['name'].isin(cities)]
            df_demand = df_demand[df_demand['city'].isin(cities)]

            df_demand['region'] = df_demand['city'].apply(lambda x: city2region[x])
            df_demand = df_demand[['time', 'region', 'type', 'count']].groupby(['time', 'region', 'type']).sum().reset_index()

            df_supply['region'] = df_supply['name'].apply(lambda x: city2region[x])
            df_supply = df_supply[['time', 'region', 'type', 'flow_in_net_country_norm']].groupby(['time', 'region', 'type']).sum().reset_index()
            
            df_demand = get_ratio_column(df_demand)
            df_demand = df_demand[df_demand['type']!='其他']
            df_demand = get_rank_column(df_demand, score_col='ratio').sort_values(by=['time', 'region', 'rank'])
            df_supply = get_rank_column(df_supply, score_col='flow_in_net_country_norm').sort_values(by=['time', 'region', 'rank'])
            df_supply = df_supply[df_supply['type']!='其他']

            df_demand.to_csv('{}/{}/demand_{}_{}.csv'.format(OUT_MISMATCH_PATH, mode, mode, graph_name), index=False)
            df_supply.to_csv('{}/{}/supply_{}_{}.csv'.format(OUT_MISMATCH_PATH, mode, mode, graph_name), index=False)