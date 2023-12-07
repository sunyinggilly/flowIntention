import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
sys.path.append('../../../../')
import pandas as pd
from CONFIG import *


def get_level_dict():
    df_city_level = pd.read_csv("%s/city/city_level_2020.csv" % DATA_PATH)
    level_dct = {}
    for city, level in df_city_level.values.tolist():
        level_dct[city] = level
    return level_dct


def read_translation():
    df = pd.read_csv("%s/city/name_translation.csv" % DATA_PATH)
    dct = {}
    for name, en_name in df.values.tolist():
        dct[name] = en_name
    return dct


def get_timelst(tfrom, tto):
    tnow_year, tnow_month = tfrom
    tend_year, tend_month = tto
    lst = ['%d%02d' % (tnow_year, tnow_month)]
    while tnow_year != tend_year or tnow_month != tend_month:
        tnow_year += tnow_month // 12
        tnow_month = tnow_month % 12 + 1
        lst.append(month_str(tnow_year, tnow_month))
    return lst


def month_str(year, month):
    return '%d%02d' % (year, month)


def season_str(year, month):
    return '%dQ%d' % (year, (month - 1) // 3 + 1)


def read_graph(coarse_time='month', coarse='province', time_from=(2019, 10), time_end=(2020, 5), self_edge=False):
    df = pd.DataFrame()
    for timestr in get_timelst(time_from, time_end):
        df_tmp = pd.read_csv("%s/%s.csv" % (TRANS_PATH, timestr))
        df = df.append(df_tmp)

    if coarse_time == 'month':
        df['time'] = df['time'].apply(lambda x: month_str(int(x[:4]), int(x[5:].split('-')[0])))
        pretime = month_str(time_from[0] - 1, 12) if time_from[1] == 1 else month_str(time_from[0], time_from[1] - 1)
    elif coarse_time == 'season' or coarse_time == 'all':
        df['time'] = df['time'].apply(lambda x: season_str(int(x[:4]), int(x[5:].split('-')[0])))
        pretime = season_str(time_from[0] - 1, 12) if time_from[1] == 1 else season_str(time_from[0], time_from[1] - 1)
        lastseason = season_str(time_end[0] + time_end[1] // 12, time_end[1] % 12 + 1)
        df = df[df['time'] != lastseason]
    df = df[df['time'] != pretime]
    if coarse_time == 'all':
        df['time'] = 'all'
    df = df[['time', '%s_from' % coarse, '%s_to' % coarse, 'count']]
    df = df.groupby(['time', '%s_from' % coarse, '%s_to' % coarse]).sum().reset_index()
    df = df.rename(columns={'%s_from' % coarse: 'from', '%s_to' % coarse: 'to'}, inplace=False)
    df = df[(df['from'] != 'NuLL') & (df['to'] != 'NuLL')]
    if not self_edge:
        df = df[df[['from', 'to']].apply(lambda x: x[0] != x[1], axis=1)]
    return df


def read_graph_from_file(coarse='province', self_edge=False, graph_name='season'):
    df = pd.read_csv("%s/%s/graph/%s.csv" % (ANA_DATA_PATH, graph_name, coarse))
    df = df[(df['from'] != 'NuLL') & (df['to'] != 'NuLL')]
    if not self_edge:
        df = df[df[['from', 'to']].apply(lambda x: x[0] != x[1], axis=1)]
    return df


def read_location(coord_sys='ll', coarse='km'):
    df_pos = pd.read_csv("%s/address_location_%s.csv" % (CITY_DATA_PATH, coord_sys))
    if coord_sys == 'mc' and coarse == 'km':
        df_pos['mc_x'] = df_pos['mc_x'].apply(lambda x: x / 1000)
        df_pos['mc_y'] = df_pos['mc_y'].apply(lambda x: x / 1000)
    return df_pos
