import sys
sys.path.append('/code')
import pandas as pd
from CONFIG import *
from Utils.tools import make_path


def get_season(x):
    x = x.split('-')
    return '{}Q{}'.format(x[0], (int(x[1]) - 1) // 3 + 1)

dct = {'高中': '高中及以下', '初中': '高中及以下', '小学': '高中及以下', '不限': '高中及以下', '大专':'大专', '博士': '本科及以上', '硕士': '本科及以上', '本科': '本科及以上'}
if __name__ == "__main__":
    make_path('%s/edu' % OUT_MISMATCH_PATH)

    df_trans_edu = pd.read_csv('%s/edu.csv' % DATA_TRANS_TYPE_PATH)

    df_trans_edu['time'] = df_trans_edu['date'].apply(lambda x: '-'.join(x.split('-')[:2]))
    df_trans_edu = df_trans_edu.drop('date', axis=1)
    df_trans_edu = df_trans_edu.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans_edu.to_csv('%s/edu/transition_month.csv' % OUT_MISMATCH_PATH, index=False)
    df_trans_edu['time'] = df_trans_edu['time'].apply(get_season)
    df_trans_edu = df_trans_edu.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans_edu.to_csv('%s/edu/transition_season.csv' % OUT_MISMATCH_PATH, index=False)
    
    df_trans_edu['time'] = 'all'
    df_trans_edu = df_trans_edu.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans_edu.to_csv('%s/edu/transition_all.csv' % OUT_MISMATCH_PATH, index=False)
    
    df_edu = pd.read_csv('%s/edu.csv' % DATA_JD_TYPE_PATH)[['time', 'province', 'city', 'type', 'count']]
    df_edu['time'] = df_edu['time'].apply(lambda x: '{}-{}'.format(x // 100, x % 100))
    df_edu = df_edu.groupby(['time', 'province', 'city', 'type']).sum().reset_index()
    df_edu['type'] = df_edu['type'].apply(lambda x: dct[x])
    df_edu.to_csv('%s/edu/jd_month.csv' % OUT_MISMATCH_PATH, index=False)

    df_edu['time'] = df_edu['time'].apply(get_season)
    df_edu = df_edu.groupby(['time', 'province', 'city', 'type']).sum().reset_index()
    df_edu.to_csv('%s/edu/jd_season.csv' % OUT_MISMATCH_PATH, index=False)

    df_edu['time'] = 'all'
    df_edu = df_edu.groupby(['time', 'province', 'city', 'type']).sum().reset_index()
    df_edu.to_csv('%s/edu/jd_all.csv' % OUT_MISMATCH_PATH, index=False)
