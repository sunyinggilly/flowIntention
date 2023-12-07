import sys
sys.path.append('/code')
from CONFIG import *
from Utils.util_read import read_graph_from_file
from Utils.util_read import read_translation, get_level_dict
from Utils.tools import make_path
import pandas as pd
import seaborn as sns
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
    df = pd.merge(df, df_all, on=['time', 'region']) # [time, city, type, count, all]
    df['ratio'] = df['count'] / df['all']
    return df.drop('all', axis=1)

if __name__ == "__main__":

    df_statistics = pd.read_csv("%s/city/city_statistics.csv" % DATA_PATH)
    df_statistics_2023_fake = df_statistics[df_statistics['年份'] == 2021]
    df_statistics_2023_fake['年份'] = 2022

    df_statistics = df_statistics.append(df_statistics_2023_fake)
    df_statistics = df_statistics[['年份', '地区', '职工平均工资(元)']]
    df_statistics['地区'] = df_statistics['地区'].apply(lambda x: x + '市')

    for SELF in [True, False]:
        for mode in ['salary']:
            for graph_name in ['season', 'month']:
                df = pd.read_csv('{}/{}/transition_{}.csv'.format(OUT_MISMATCH_PATH, mode, graph_name))[['time', 'value', 'city_from', 'city_to', 'count']]
                if not SELF:
                    df = df[df['city_from'] != df['city_to']]
                df.rename(columns={'city_from': 'from', 'city_to': 'to'}, inplace=True)

                df['time'] = df['time'].astype(str)
                df['year'] = df['time'].apply(lambda x: int(x[:4]))

                df = pd.merge(df, df_statistics, left_on=['year', 'from'], right_on=['年份', '地区'], how='inner').drop(['年份', '地区'], axis=1)
                df.rename(columns={'职工平均工资(元)': 'from_salary'}, inplace=True)
                df = pd.merge(df, df_statistics, left_on=['year', 'to'], right_on=['年份', '地区'], how='left').drop(['年份', '地区'], axis=1)
                df.rename(columns={'职工平均工资(元)': 'to_salary'}, inplace=True)

                # 如果 to_salary为NaN则补0，即认为工资和当前一样
                df['salary_diff_weighted'] = df[['from_salary', 'to_salary', 'count']].apply(lambda x: (x[1] - x[0]) * x[2], axis=1).fillna(0)

                df_city = df[['time', 'value', 'from', 'salary_diff_weighted', 'count']].groupby(['time', 'from', 'value']).sum()
                df_city['average_salary_diff'] = df_city.apply(lambda x: x[0] / x[1], axis=1)
                df_city = df_city.reset_index()
                df_city = df_city[df_city['count'] > 100]
                df_city = df_city[['time', 'from', 'value', 'average_salary_diff', 'salary_diff_weighted', 'count']]
                df_city.rename(columns={'from': 'name'}, inplace=True)

                make_path('%s/%s/centrality_with_income' % (OUT_INCOME_PATH, graph_name))
                df_city.to_csv('%s/%s/centrality_with_income/city_income_diff_%s_%s.csv' % (OUT_INCOME_PATH, graph_name, mode, SELF), index=False)
                