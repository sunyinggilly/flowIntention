import sys
sys.path.append('/code')
import networkx as nx
import pandas as pd
from CONFIG import ANA_DATA_PATH, OUT_MISMATCH_PATH
from tqdm import tqdm
from Utils.util_read import read_location, get_timelst
from CoordGraph import CoordGraph, build_graph
from Utils.tools import make_path

def read_graph_from_file(path, coarse='province', self_edge=False):
    df = pd.read_csv(path)
    df = df[(df['%s_from' % coarse] != 'NuLL') & (df['%s_to' % coarse] != 'NuLL')]
    if not self_edge:
        df = df[df[['%s_from' % coarse, '%s_to' % coarse]].apply(lambda x: x[0] != x[1], axis=1)]
    df[['time', '%s_from' % coarse, '%s_to' % coarse, 'count']]
    df.rename(columns={'%s_from' % coarse: 'from', '%s_to' % coarse: 'to'}, inplace=True)
    df = df.groupby(['time', 'from', 'to', 'value']).sum().reset_index()
    return df

def solve(df_graph, df_loc, pr_hits=True):
    time_lst = df_graph['time'].drop_duplicates().tolist()
    df = pd.DataFrame()
    for timestr in time_lst:
        df_now = df_graph[df_graph['time'] == timestr][['from', 'to', 'count']]
        cg = build_graph(df_now, df_loc, places=None)
        df_now = cg.calc_centrality(pr_hits=pr_hits)
        df_now['time'] = timestr
        df = df.append(df_now)
    cols = df.drop(['time', 'name'], axis=1).columns
    return df

def gross_flow_solve(df):
    df_self = df.drop('to', axis=1).groupby(['from', 'time']).sum().reset_index()
    df_out = df[df['from'] != df['to']].drop('to', axis=1).groupby(['from', 'time']).sum().reset_index()
    df = pd.merge(df_self, df_out, on=['time', 'from'], how='outer').fillna(0)
    df['gross_flow'] = df['count_y'] / df['count_x']
    df.rename(columns={'from': 'name'}, inplace=True)
    
    return df.drop(['count_x', 'count_y'], axis=1)

def get_flowin_norm_with_self(df_cent, df_self_trans):
    df_now = df_cent[['time', 'name', 'value', 'flow_in', 'flow_out', 'flow_in_net']]
    df_norm = df_self_trans.drop(['from', 'to', 'value'], axis=1) # time, from, count
    df_norm = df_norm.groupby(['time']).sum().reset_index() # time, count
    df_now = pd.merge(df_now, df_norm, on=['time'])
    for col in ['flow_in', 'flow_out', 'flow_in_net']:
        df_now[col + 'norm_with_selfflow'] = df_now[col] / df_now['count']
    return df_now.drop('count', axis=1)

def normalize(df, cols, norm_type='country', df_self=None):
    # name, time, value, centralities
    df_now = df[['name', 'time', 'value'] + cols]
    if norm_type == 'country':
        df_norm = df_now.drop(['name', 'value'], axis=1)
        df_norm = df_norm.groupby(['time']).sum().reset_index()
        df_now = pd.merge(df_now, df_norm, on=['time'])
    else:
        df_norm = df_now.drop(['value'], axis=1)
        df_norm = df_norm.groupby(['time', 'name']).sum().reset_index()
        df_now = pd.merge(df_now, df_norm, on=['time', 'name'])   

    drop_lst = []
    for col in cols:
        df_now['{}_{}_norm'.format(col, norm_type)] = df_now[col+'_x'] * 1000 / df_now[col+'_y']
        drop_lst.extend([col + '_x', col + '_y'])
    return df_now.drop(drop_lst, axis=1)


def side_data_prepare(mode):
    df_prepare = read_graph_from_file(path='{}/{}/transition_season.csv'.format(OUT_MISMATCH_PATH, mode), coarse='province', self_edge=False)
    value_list = df_prepare['value'].drop_duplicates().tolist()

    df_loc_mc = read_location(coord_sys='mc', coarse='km')
    df_loc_ll = read_location(coord_sys='ll', coarse=None)
    df_loc = pd.merge(df_loc_mc, df_loc_ll, on=['name'])[['name', 'll_x', 'll_y', 'mc_x', 'mc_y']]
    return value_list, df_loc


if __name__ == "__main__":
    norm_cols = ['flow_in', 'flow_out', 'all_flow_in', 'all_flow_out', 'jdcount']
    for mode in ['edu', 'industry']:
        value_list, df_loc = side_data_prepare(mode)
        for coarse in ['city']:
            for GRAPH_NAME in ['all', 'month', 'season']:
                df = read_graph_from_file(path='{}/{}/transition_{}.csv'.format(OUT_MISMATCH_PATH, mode, GRAPH_NAME), 
                                          coarse=coarse, self_edge=False)
                df_self = read_graph_from_file(path='{}/{}/transition_{}.csv'.format(OUT_MISMATCH_PATH, mode, GRAPH_NAME), 
                                               coarse=coarse , self_edge=True)
                make_path('%s/%s/centrality/%s' % (OUT_MISMATCH_PATH, mode, coarse))
                df_centrality = pd.DataFrame()

                for value in tqdm(value_list):
                    df_now = df[df['value'] == value].drop('value', axis=1)
                    df_self_now = df_self[df_self['value']== value].drop('value', axis=1)
                    
                    df_centrality_now = solve(df_now, df_loc)
                    df_gflow_now = gross_flow_solve(df_self_now)          
                    df_centrality_self_now = solve(df_self_now, df_loc, pr_hits=False)

                    df_centrality_self_now.rename(columns={'flow_in': 'all_flow_in', 'flow_out': 'all_flow_out'}, inplace=True)
                    df_centrality_self_now = df_centrality_self_now[['name', 'time', 'all_flow_in', 'all_flow_out']]
                    
                    df_centrality_now = pd.merge(df_centrality_now, df_gflow_now, on=['name', 'time'], how='outer').fillna(0)
                    df_centrality_now = pd.merge(df_centrality_now, df_centrality_self_now, on=['name', 'time'], how='outer').fillna(0)
                    df_centrality_now['value'] = value

                    df_centrality = df_centrality.append(df_centrality_now)

                df_jd = pd.read_csv('%s/%s/jd_%s.csv' % (OUT_MISMATCH_PATH, mode, GRAPH_NAME))
                df_jd = df_jd[['time', coarse, 'type', 'count']]
                df_jd.rename(columns={coarse: 'name', 'type': 'value', 'count': 'jdcount'}, inplace=True)
                df_jd = df_jd.groupby(['time', 'name', 'value']).sum().reset_index()
                df_centrality = pd.merge(df_centrality, df_jd, on=['time', 'name', 'value'])
                
                df_country_norm = normalize(df_centrality, norm_cols, norm_type='country')
                df_name_norm = normalize(df_centrality, norm_cols, norm_type='name')

                df_centrality = pd.merge(df_centrality, df_country_norm, on=['name', 'time', 'value'], how='outer').fillna(0)
                df_centrality = pd.merge(df_centrality, df_name_norm, on=['name', 'time', 'value'], how='outer').fillna(0)

                df_centrality['flow_in_net_country_norm'] = df_centrality['flow_in_country_norm'] - df_centrality['flow_out_country_norm'] 
                df_centrality['flow_in_net_name_norm'] = df_centrality['flow_in_name_norm'] - df_centrality['flow_out_name_norm']
                
                df_flow_normed = get_flowin_norm_with_self(df_centrality, df_self)
                df_centrality.to_csv('%s/%s/centrality/%s/%s.csv' % (OUT_MISMATCH_PATH, mode, coarse, GRAPH_NAME), index=False)
