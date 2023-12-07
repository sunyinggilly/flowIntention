import sys
sys.path.append('/code')
from CONFIG import *
from Utils.util_read import get_level_dict
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
    df = pd.merge(df, df_all, on=['time', 'region']) 
    df['ratio'] = df['count'] / df['all']
    return df.drop('all', axis=1)

if __name__ == "__main__":
    Q = '4'
    path = OUT_INCOME_PATH

    df_statistics = pd.read_csv("%s/city/city_statistics.csv" % DATA_PATH)
    df_statistics_2023_fake = df_statistics[df_statistics['年份']==2021]
    df_statistics_2023_fake['年份'] = 2022

    df_statistics = df_statistics.append(df_statistics_2023_fake)
    df_statistics = df_statistics[['年份', '地区', '职工平均工资(元)']]
    df_statistics['地区'] = df_statistics['地区'].apply(lambda x: x + '市')
    for SELF in [True]:
        for mode in ['salary']:
            for graph_name in ['season']:
                df_city = pd.read_csv('%s/%s/centrality_with_income/city_income_diff_%s_%s.csv' % (path, graph_name, mode, SELF))[['time', 'name', 'value', 'average_salary_diff', 'salary_diff_weighted', 'count']]
                level_lst = ['Tier 1', 'New tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
                level_dct = get_level_dict()
                df_city['Tier'] = df_city['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)

                value_lst = df_city['value'].drop_duplicates().tolist()
                for value in value_lst:
                    df_now = df_city[df_city['value'] == value]

                    df_tier = df_now[df_now['Tier'] != -1]
                    df_tier = df_tier[['time', 'Tier', 'salary_diff_weighted', 'count']].groupby(['time', 'Tier']).sum()
                    df_tier['average_salary_diff'] = df_tier.apply(lambda x: x[0] / x[1], axis=1)
                    df_tier = df_tier.reset_index()
                    df_tier = df_tier.sort_values(by=['Tier', 'time'])
                    df_tier['Tier'] = df_tier['Tier'].apply(lambda x: level_lst[x])    
                    

                    if graph_name == 'season' and Q is not None:
                        df_tier = df_tier[df_tier['time'].apply(lambda x: x.split('Q')[1] == Q)]

                    df_tier['average_salary_diff'] = df_tier['average_salary_diff'] / 1000
                    df_tier = df_tier.rename(columns={'average_salary_diff': 'Salary Difference (1000 CNY)', 'time': 'Time'})
                    df_tier1 = df_tier[df_tier['Tier'] == 'Tier 1']
                    
                    sns.lineplot(data=df_tier1, hue='Tier', y='Salary Difference (1000 CNY)', x='Time', ci=95)
                    sns.scatterplot(data=df_tier1, hue='Tier', y='Salary Difference (1000 CNY)', x='Time', s=50, legend=False)
                    plt.ylim(-26, -13)
                    if graph_name == 'month':
                        plt.xticks(rotation=45) 
                    plt.savefig('%s/%s/centrality_with_income/city_income_diff_%s_%s_%s_%s_t1.png' % (path, graph_name, mode, value, SELF, Q))
                    plt.close()

                    df_tier = df_tier[df_tier['Tier'] != 'Tier 1']
                    lineplt = sns.lineplot(data=df_tier, hue='Tier', y='Salary Difference (1000 CNY)', x='Time', ci=95)
                    sns.scatterplot(data=df_tier, hue='Tier', y='Salary Difference (1000 CNY)', x='Time', s=50, legend=False)

                    lineplt.legend(loc='best', ncol=3, fancybox=True)
                    if graph_name == 'month':
                        plt.xticks(rotation=45) 
                    plt.savefig('%s/%s/centrality_with_income/city_income_diff_%s_%s_%s_%s_t2.png' % (path, graph_name, mode, value, SELF, Q))
                    plt.close()
                    