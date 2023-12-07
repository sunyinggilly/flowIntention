import sys
sys.path.append('/code')
import pandas as pd
from CONFIG import *
from Utils.tools import make_path


def get_level_dict():
    df_city_level = pd.read_csv("%s/city/city_level_2020.csv" % DATA_PATH)
    level_dct = {}
    for city, level in df_city_level.values.tolist():
        level_dct[city] = level
    return level_dct

if __name__ == "__main__":
    df_kmeans = pd.read_csv("%s/season/jd/city_kmeans.csv" % ANA_DATA_PATH)
    print(df_kmeans['jd_All'].sum())
    # print(df_kmeans)

    # 2019Q4 - 2020Q4 bluecollar in whole country
    df = df_kmeans[['name', 'time', 'jd_Blue Collar', 'jd_All', 'jd_Public Transit Staff']]
    df_2019Q4 = df[df['time'] == '2019Q4']
    df_2020Q4 = df[df['time'] == '2020Q4']
    df_2021Q4 = df[df['time'] == '2021Q4']
    df_2020Q1 = df[df['time'] == '2020Q1']
    df_2020Q2 = df[df['time'] == '2020Q2']

    # all
    blue_count_2019Q4 = df_2019Q4.drop(['name', 'time'], axis=1).sum()['jd_Blue Collar']
    blue_count_2020Q4 = df_2020Q4.drop(['name', 'time'], axis=1).sum()['jd_Blue Collar']
    blue_count_2021Q4 = df_2021Q4.drop(['name', 'time'], axis=1).sum()['jd_Blue Collar']
    public_count_2021Q4 = df_2021Q4.drop(['name', 'time'], axis=1).sum()['jd_Public Transit Staff']

    print("increase of blue collar count from 2019Q4 to 2020Q4", blue_count_2020Q4/blue_count_2019Q4 - 1) 
    print("ratio of blue collar count of 2021Q4 to 2019Q4", blue_count_2021Q4/blue_count_2019Q4)  
    print("ratio of 2021Q4 public transit staff to 2019Q4 blue collar count", public_count_2021Q4/blue_count_2019Q4) 

    # tier
    level_dct = get_level_dict()

    df_2019Q4['name'] = df_2019Q4['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_2019Q4 = df_2019Q4[df_2019Q4['name'] != -1]

    df_2020Q4['name'] = df_2020Q4['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_2020Q4 = df_2020Q4[df_2020Q4['name'] != -1]

    blue_count_2019Q4 = df_2019Q4.drop('time', axis=1).groupby(['name']).sum()['jd_Blue Collar']
    blue_count_2020Q4 = df_2020Q4.drop('time', axis=1).groupby(['name']).sum()['jd_Blue Collar']
    print(blue_count_2020Q4/blue_count_2019Q4 - 1)

    # ratio of public transit staff to blue collar in different tiers
    df_tmp = df_2019Q4.groupby(['name']).sum()[['jd_Blue Collar', 'jd_Public Transit Staff']]
    df_tmp['ratio'] = df_tmp[['jd_Blue Collar', 'jd_Public Transit Staff']].apply(lambda x: x[1]/x[0], axis=1)
    print(df_tmp[ 'ratio'])

    # blue increase from 2020Q1 to 2020Q2
    level_dct = get_level_dict()

    df_2020Q1['name'] = df_2020Q1['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_2020Q1 = df_2020Q1[df_2020Q1['name'] != -1]

    df_2020Q2['name'] = df_2020Q2['name'].apply(lambda x: level_dct[x] if x in level_dct else -1)
    df_2020Q2 = df_2020Q2[df_2020Q2['name'] != -1]

    blue_count_2020Q1 = df_2020Q1.drop('time', axis=1).groupby(['name']).sum()['jd_Blue Collar']
    blue_count_2020Q2 = df_2020Q2.drop('time', axis=1).groupby(['name']).sum()['jd_Blue Collar']
    print(blue_count_2020Q2/blue_count_2020Q1 - 1)
