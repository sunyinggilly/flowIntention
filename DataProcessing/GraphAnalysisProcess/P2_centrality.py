import sys
sys.path.append('/code')
import networkx as nx
import pandas as pd
from CONFIG import ANA_DATA_PATH
from Utils.tools import make_path
from tqdm import tqdm
from Utils.util_read import read_graph_from_file, read_location
from CoordGraph import build_graph


def gross_flow_solve(df):
    df_self = df.drop('to', axis=1).groupby(['from', 'time']).sum().reset_index()
    df_out = df[df['from'] != df['to']].drop('to', axis=1).groupby(['from', 'time']).sum().reset_index()
    df = pd.merge(df_self, df_out, on=['time', 'from'], how='outer').fillna(0)
    df['gross_flow'] = df['count_y'] / df['count_x']
    df.rename(columns={'from': 'name'}, inplace=True)
    
    return df.drop(['count_x', 'count_y'], axis=1)

def flow_net_in_country_norm(df):
    # time, from, to, count
    df_to = df[['time', 'to', 'count']]
    df_from = df[['time', 'from', 'count']]
    df_to = df_to.groupby(['time', 'to']).sum().reset_index().rename(columns={'to': 'name', 'count': 'in'}) # time, to, count
    df_from = df_from.groupby(['time', 'from']).sum().reset_index().rename(columns={'from': 'name', 'count': 'out'}) # time, from, count
    df_all = df_to.groupby(['time']).sum().reset_index().rename(columns={'in':'all'}) # time, count
    df = pd.merge(df_all, df_to, on=['time'], how='outer').fillna(0)
    df = pd.merge(df, df_from, on=['time', 'name'], how='outer').fillna(0)
    df = df[['time', 'name', 'in', 'out', 'all']]
    df['flow_in_net_country_norm'] = df[['in', 'out', 'all']].apply(lambda x: (x[0] - x[1]) * 1000 / x[2], axis=1)
    return df[['time', 'name', 'flow_in_net_country_norm']]


def solve(df_graph, df_loc):
    time_lst = df_graph['time'].drop_duplicates().tolist()
    df = pd.DataFrame()
    for timestr in tqdm(time_lst):
        df_now = df_graph[df_graph['time'] == timestr][['from', 'to', 'count']]
        cg = build_graph(df_now, df_loc, places=None)
        df_now = cg.calc_centrality()
        df_now['time'] = timestr
        df = df.append(df_now)
    return df


if __name__ == "__main__":
    df_loc_mc = read_location(coord_sys='mc', coarse='km')
    df_loc_ll = read_location(coord_sys='ll', coarse=None)
    df_loc = pd.merge(df_loc_mc, df_loc_ll, on=['name'])[['name', 'll_x', 'll_y', 'mc_x', 'mc_y']]
    for GRAPH_NAME in ['season', 'month', 'all']:
        for coarse in ['province', 'city']:
            make_path('%s/%s/centrality/' % (ANA_DATA_PATH, GRAPH_NAME))
            df = read_graph_from_file(coarse=coarse, self_edge=False, graph_name=GRAPH_NAME)
            df_self = read_graph_from_file(coarse=coarse, self_edge=True, graph_name=GRAPH_NAME)
            df_centrality = solve(df, df_loc)

            df_gflow = gross_flow_solve(df_self)
            df_netflow = flow_net_in_country_norm(df_self)
            
            df = pd.merge(df_gflow, df_netflow, on=['time', 'name'])
            df_centrality = pd.merge(df_centrality, df, on=['time', 'name'], how='outer').fillna(0)

            df_centrality.to_csv('%s/%s/centrality/%s_centrality.csv' % (ANA_DATA_PATH, GRAPH_NAME, coarse), index=False)