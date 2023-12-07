import sys
sys.path.append('/code')
import pandas as pd
from CONFIG import *
from Utils.tools import make_path


def get_season(x):
    x = x.split('-')
    return '{}Q{}'.format(x[0], (int(x[1]) - 1) // 3 + 1)


trans_industry_projection = {
    '教育':'教育',
    '法律商务人力外贸': '法律商务人力外贸',
    '医药卫生':'医药卫生',
    '能源采矿化工':'工业与制造',
    '食品加工': '工业与制造',
    '机械制造':'工业与制造',
    '住宿旅游':'住宿旅游',
    'IT通信电子':'IT',
    '文化体育娱乐': '文化体育娱乐',
    '农林牧渔':'农林牧渔',
    '金融保险':'金融保险',
    '建筑房地产':'房产建筑',
    '建材家居':'房产建筑',
    '交通运输和仓储邮政':'交通仓储',
    '日化百货':'日化百货-消费零售-服装',
    '纺织服装': '日化百货-消费零售-服装',
    '家电': '日化百货-消费零售-服装',
    '餐饮': '餐饮',
    '汽车':'汽车',
    '生活服务': '生活服务',
    '广告营销': '广告营销',
    '社会公共管理':'社会公共管理',
}

jd_industry_projection = {
    '教育':'教育',
    '商务服务':'商务服务',
    '医药卫生':'医药卫生',
    '工业与制造':'工业与制造',
    '住宿旅游':'住宿旅游',
    'IT':'IT',
    '文化体育娱乐':'文化体育娱乐',
    '农林牧渔':'农林牧渔',
    '金融保险':'金融保险',
    '房产建筑':'房产建筑',
    '交通仓储':'交通仓储',
    '日化百货-消费零售-服装':'日化百货-消费零售-服装',
    '餐饮':'餐饮',
    '汽车':'汽车',
    '生活服务':'生活服务',
    '广告营销':'广告营销',
    '其他':'其他'
}
if __name__ == "__main__":
    make_path('%s/industry' % OUT_MISMATCH_PATH)

    df_trans = pd.read_csv('%s/industry.csv' % DATA_TRANS_TYPE_PATH)
    df_trans['value'] = df_trans['value'].apply(lambda x: trans_industry_projection[x])
    df = pd.read_csv('%s/industry.csv' % DATA_JD_TYPE_PATH)[['time', 'province', 'city', 'type', 'count']]
    df['type'] = df['type'].apply(lambda x: jd_industry_projection[x])

    df_trans['time'] = df_trans['date'].apply(lambda x: '-'.join(x.split('-')[:2]))
    df_trans = df_trans.drop('date', axis=1)
    df_trans = df_trans.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans.to_csv('%s/industry/transition_month.csv' % OUT_MISMATCH_PATH, index=False)
    df_trans['time'] = df_trans['time'].apply(get_season)
    df_trans = df_trans.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans.to_csv('%s/industry/transition_season.csv' % OUT_MISMATCH_PATH, index=False)
    
    df_trans['time'] = 'all'
    df_trans = df_trans.groupby(['time','province_from','city_from','province_to','city_to', 'value']).sum().reset_index()
    df_trans.to_csv('%s/industry/transition_all.csv' % OUT_MISMATCH_PATH, index=False)
    
    df['time'] = df['time'].apply(lambda x: '{}-{}'.format(x // 100, x % 100))
    df = df.groupby(['time', 'province', 'city', 'type']).sum().reset_index()
    df.to_csv('%s/industry/jd_month.csv' % OUT_MISMATCH_PATH, index=False)

    df['time'] = df['time'].apply(get_season)
    df = df.groupby(['time', 'province', 'city', 'type']).sum().reset_index()
    df.to_csv('%s/industry/jd_season.csv' % OUT_MISMATCH_PATH, index=False)

    df['time'] = 'all'
    df = df.groupby(['time', 'province', 'city', 'type']).sum().reset_index()
    df.to_csv('%s/industry/jd_all.csv' % OUT_MISMATCH_PATH, index=False)
