import sys
sys.path.append('/code')

import pandas as pd
from CONFIG import *
from Utils.util_read import season_str, month_str
from Utils.tools import make_path


def read_city2province():
    df = pd.read_csv("%s/city/areas.csv" % DATA_PATH)
    df = df[df['city'] != 'NuLL']
    city2province = {'台湾省': '台湾省'}
    for city, province in df[['city', 'province']].values.tolist():
        city2province[city] = province
    return city2province


def jd_centrality(df_jd, job_cate_funcs):  # name, time, word, count
    df_all = None
    # dicts
    for category, cat_list in job_cate_funcs.items():
        df_now = df_jd[df_jd['topic'].apply(lambda x: x in cat_list)]

        df_now_all = df_now[['name', 'time', 'count']].groupby(['name', 'time']).sum().reset_index()
        df_now_all.rename(columns={'count': 'jd_%s' % category}, inplace=True)

        # 每个时间段可视化
        time_sum = {}
        group_ser = df_now_all[['time', 'jd_%s' % category]].groupby('time')
        for time, count_sum in group_ser.sum().reset_index().values.tolist():
            time_sum[time] = count_sum

        df_now_all['jd_%s_norm' % category] = df_now_all[['time', 'jd_%s' % category]].apply(lambda x: x[1] / time_sum[x[0]], axis=1)
        df_all = pd.merge(df_all, df_now_all, on=['name', 'time'], how='left').fillna(0) if df_all is not None else df_now_all
    return df_all


def get_job_cate_funcs():
    return {'All': list(range(30)), # Express-6,删除
            'Public Transit Staff': [1, 5, 19, 22, 24], 'Transporter': [18], 'Security': [23],
            'Blue Collar': [1, 5, 19, 22, 24, 0, 3, 4, 7, 11, 12, 17, 18, 25, 26, 29],
            'Factory Worker': [0, 3, 4, 7, 11, 12, 17, 25, 26, 29], 
             # 'SkilledWorder': [4],
            'Clerk': [8, 27], 'Merchandiser': [14], 'Salesman': [20, 28],
            'Beautician': [15],
            'Designer': [9], 'Manager': [2, 16], 'Engineer': [21], 'White Collar': [2, 9, 16, 21]}



if __name__ == "__main__":

    make_path("%s/month/jd/" % ANA_DATA_PATH)
    make_path("%s/season/jd/" % ANA_DATA_PATH)
    make_path("%s/all/jd/" % ANA_DATA_PATH)

    job_cate_funcs = get_job_cate_funcs()
    city2province = read_city2province()
    df = pd.read_csv("%s/JDData/city_kmeans.csv" % DATA_PATH)  # city, time, K0, ...
    df['city'] = df['city'].fillna(-1)
    df = df[df['city'] != -1]
    df['province'] = df['city'].apply(lambda x: city2province[x])
    df = df[df['province'] != -1]

    # for month
    df['time'] = df['time'].apply(lambda x: month_str(int(str(x)[:4]), int(str(x)[4:6])))
    df_province = jd_centrality(df[['province', 'time', 'topic', 'count']].rename(columns={'province': 'name'}, inplace=False), job_cate_funcs=job_cate_funcs)
    df_city = jd_centrality(df[['city', 'time', 'topic', 'count']].rename(columns={'city': 'name'}, inplace=False), job_cate_funcs=job_cate_funcs)
    df_province.to_csv("%s/month/jd/province_kmeans.csv" % ANA_DATA_PATH, index=False)
    df_city.to_csv("%s/month/jd/city_kmeans.csv" % ANA_DATA_PATH, index=False)

    # for season
    df['time'] = df['time'].apply(lambda x: season_str(int(str(x)[:4]), int(str(x)[4:6])))
    df_province = jd_centrality(df[['province', 'time', 'topic', 'count']].rename(columns={'province': 'name'}, inplace=False), job_cate_funcs=job_cate_funcs)
    df_city = jd_centrality(df[['city', 'time', 'topic', 'count']].rename(columns={'city': 'name'}, inplace=False), job_cate_funcs=job_cate_funcs)
    df_province.to_csv("%s/season/jd/province_kmeans.csv" % ANA_DATA_PATH, index=False)
    df_city.to_csv("%s/season/jd/city_kmeans.csv" % ANA_DATA_PATH, index=False)

    # for all
    df['time'] = 'all'
    df_province = jd_centrality(df[['province', 'time', 'topic', 'count']].rename(columns={'province': 'name'}, inplace=False), job_cate_funcs=job_cate_funcs)
    df_city = jd_centrality(df[['city', 'time', 'topic', 'count']].rename(columns={'city': 'name'}, inplace=False), job_cate_funcs=job_cate_funcs)
    df_province.to_csv("%s/all/jd/province_kmeans.csv" % ANA_DATA_PATH, index=False)
    df_city.to_csv("%s/all/jd/city_kmeans.csv" % ANA_DATA_PATH, index=False)
