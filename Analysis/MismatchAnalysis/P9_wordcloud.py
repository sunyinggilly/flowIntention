import sys
sys.path.append('/code')
from CONFIG import *
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random 
plt.switch_backend('agg')
from Utils.tools import make_path

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

def draw(df, region, time, path):
    df_now = df[(df['region'] == region) & (df['time'] == time)][['type', 'rank_diff']]
    dct = {}
    for tp, val in df_now.values.tolist():
        dct[tp] = val
    make_path('{}/{}/mismatch'.format(path, mode, region, time))
    word_cloud(dct, '{}/{}/mismatch/{}_{}.png'.format(path, mode, region, time))


def word_cloud(frequency_dict, out_path):
    def color_func(word, **kwargs):
        value = frequency_dict[word]
        if value > 0:
            # For positive values, generate a random shade of red
            return "rgb(%d, %d, 0)" % (random.randint(0, 100)+155, random.randint(0, 80))  # Keeping other values less than 255 to maintain the red shade
        else:
            # For negative values, generate a random shade of blue
            return "rgb(0, %d, %d)" % (random.randint(0, 80), random.randint(0, 100)+155)  # Keeping other values less than 255 to maintain the blue shade

    # 调整字典，使得词云的字体大小反映频率的绝对值
    adjusted_freq_dict = {word: abs(freq) for word, freq in frequency_dict.items()}

    wc = WordCloud(background_color='white',  # 背景颜色 #EEEEEE
                   #max_words=100,  # 最大词数
                   width=200,
                   height=200,
                #    min_font_size = 10,       
                   color_func=color_func,
                   scale=4
                   # mask=mask
                   )

    wc.generate_from_frequencies(adjusted_freq_dict)
    wc.to_file(out_path)

industry_translate = {'IT': 'IT', '商务服务': 'Business Service', '文化体育娱乐': 'Entertainment', 
                      '金融保险': 'FinInsur', 
                      '医药卫生': 'Healthcare', '日化百货-消费零售-服装': 'Retail & Apparel', '教育': 'Education', 
                      '工业与制造': 'IndManu', 
                      '交通仓储': 'Logistics', '房产建筑': 'RealCon', '汽车': 'Automotive', 
                      '生活服务': 'LifeSer', '农林牧渔': 'FFHF',
                      '住宿旅游': 'TourLod', '广告营销': 'Advertising', '餐饮': 'Restaurant'}

if __name__ == "__main__":
    mode = 'industry'
    graph_name = 'season'
    time_lst = ['2019Q4', '2020Q4', '2021Q4']
    region_lst = ['BTH', 'YRD', 'PRD']
    df_demand = pd.read_csv('{}/{}/demand_{}_{}.csv'.format(OUT_MISMATCH_PATH, mode, mode, graph_name))
    df_supply = pd.read_csv('{}/{}/supply_{}_{}.csv'.format(OUT_MISMATCH_PATH, mode, mode, graph_name))
    df2 = pd.merge(df_demand, df_supply, on=['time', 'region', 'type'], suffixes=['_demand', '_supply'])
    df2['rank_diff'] = df2['rank_demand'] - df2['rank_supply']
    df2 = df2[['time', 'region', 'type', 'rank_demand', 'rank_supply', 'rank_diff']]
    df2['type'] = df2['type'].apply(lambda x: industry_translate[x])
    for region in region_lst:
        for time in time_lst:
            draw(df2, region, time, OUT_MISMATCH_PATH)
