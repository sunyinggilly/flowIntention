import sys
sys.path.append('/code')
import pandas as pd
from CONFIG import *
from Utils.tools import make_path

def get_season(x):
    x = x.split('-')
    return '{}Q{}'.format(x[0], (int(x[1]) - 1) // 3 + 1)

dct = {'2499及以下': '低于4000', '2500~3999': '低于4000', '4000~7999': '4000~7999', '8000~19999': '8000~19999', '20000及以上':'20000及以上'}

if __name__ == "__main__":
    make_path('%s/salary' % OUT_MISMATCH_PATH)

    df_trans_edu = pd.read_csv('%s/salary.csv' % DATA_TRANS_TYPE_PATH)
    df_trans_edu['time'] = df_trans_edu['date'].apply(lambda x: '-'.join(x.split('-')[:2]))
    df_trans_edu = df_trans_edu.drop('date', axis=1)

    df_trans_edu['value'] = df_trans_edu['value'].apply(lambda x: dct[x])

    df_trans_edu = df_trans_edu.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans_edu.to_csv('%s/salary/transition_month.csv' % OUT_MISMATCH_PATH, index=False)
    df_trans_edu['time'] = df_trans_edu['time'].apply(get_season)
    df_trans_edu = df_trans_edu.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans_edu.to_csv('%s/salary/transition_season.csv' % OUT_MISMATCH_PATH, index=False)

    df_trans_edu['time'] = 'all'
    df_trans_edu = df_trans_edu.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans_edu.to_csv('%s/salary/transition_all.csv' % OUT_MISMATCH_PATH, index=False)