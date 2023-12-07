import sys
sys.path.append('/code')
from CONFIG import *
from scipy.sparse import coo_matrix
import numpy as np
from math import sqrt
import pandas as pd
import networkx as nx
from sklearn.cluster import SpectralClustering
import community as community_louvain


def place_list(df_graph, df_pos):
    place_pos = set(df_pos['name'].drop_duplicates().tolist())
    place_vertex = set(df_graph['from'].drop_duplicates().tolist() + df_graph['to'].drop_duplicates().tolist())
    return list(place_pos.intersection(place_vertex))


def euc_dis(x0, x1):
    return sqrt((x0[0] - x1[0]) * (x0[0] - x1[0]) + (x0[1] - x1[1]) * (x0[1] - x1[1]))


def label_lst(lst):
    dict_id = {}
    for u, ele in enumerate(lst):
        dict_id[ele] = u
    return dict_id


def build_graph(df_graph, df_loc, places=None, normalize=False):    
    if places is None:
        places = place_list(df_graph, df_loc)
    place_id_dict = label_lst(places)

    places_set = set(places)
    df_graph = df_graph[df_graph['from'].isin(places_set) & df_graph['to'].isin(places_set)]
    
    dct_place_loc = {}
    for name, ll_x, ll_y, mc_x, mc_y in df_loc[['name', 'll_x', 'll_y', 'mc_x', 'mc_y']].values.tolist():
        dct_place_loc[name] = (ll_x, ll_y, mc_x, mc_y)

    df_graph['from'] = df_graph['from'].apply(lambda x: place_id_dict[x])
    df_graph['to'] = df_graph['to'].apply(lambda x: place_id_dict[x])
    sz = max(df_graph['from'].max(), df_graph['to'].max()) + 1
    
    A = coo_matrix((df_graph['count'].tolist(), (df_graph['from'].tolist(), df_graph['to'].tolist())), shape=[sz, sz])
    if normalize:
        deg = A.sum(axis=1) 
        deg = np.reshape(deg, [1, -1])
        deg_out = deg.tolist()[0]
        df_graph['count'] = df_graph[['from', 'to', 'count']].apply(lambda x: x[2] / deg_out[x[0]], axis=1)
        A = coo_matrix((df_graph['count'].tolist(), (df_graph['from'].tolist(), df_graph['to'].tolist())), shape=[sz, sz])
    return CoordGraph(A, dct_place_loc, places, place_id_dict)


class CoordGraph(object):
    def __init__(self, A, dct_place_loc, places, place_id_dict): 
        """
        df_graph: from, to, count
        df_loc: name, ll_x, ll_y, mc_x, mc_y
        places: a list
        """
        self.places = places
        self.place_id_dict = place_id_dict
        self.dct_place_loc = dct_place_loc
        self.A = A.todense()
        self.df = pd.DataFrame(list(zip(A.row, A.col, A.data)), columns=['from', 'to', 'count'])

        self.loc_ll = [[self.dct_place_loc[u][0], self.dct_place_loc[u][1]] for u in places]
        self.loc_mc = [[self.dct_place_loc[u][2], self.dct_place_loc[u][3]] for u in places]

        D = []
        for p1 in self.loc_mc:
            D.append([])
            for p2 in self.loc_mc:
                D[-1].append(euc_dis(p1, p2))
        self.D = np.mat(D)

        # degree
        self.deg_in = self.get_degree(in_degree=True)
        self.deg_out = self.get_degree(in_degree=False)


    def get_degree(self, in_degree=True):
        deg = self.A.sum(axis=0) if in_degree else self.A.sum(axis=1) 
        deg = np.reshape(deg, [1, -1])
        return deg.tolist()[0]


    def find_near(self, seed_pls_id, th_d):
        d_list = self.D[seed_pls_id, :].tolist()[0]
        ret = []
        for pls_id, distance in enumerate(d_list):
            if distance < th_d:
                ret.append(pls_id)
        return ret


    def get_id(self, name):
        # print(self.place_id_dict)
        return self.place_id_dict[name]


    def get_coord(self, place_list, coord_sys='ll'):
        return [self.loc_ll[self.get_id(u)] for u in place_list]

    def set_colors(self, colors):
        self.colors = colors
        self.df['color'] = self.df[['from', 'to']].apply(lambda x: colors[x[0]] if colors[x[0]] == colors[x[1]] else -1, axis=1)

    def set_vertex_weight(self, Vw):
        self.Vw = Vw

    def filter_by_edgeweight(self, threshold, filter_vertices=True):
        edge_df = self.df[self.df['count'] > threshold]
        if filter_vertices:
            vertices = set(edge_df['from'].drop_duplicates().tolist() + edge_df['to'].drop_duplicates().tolist())
        else:
            vertices = set(self.df['from'].drop_duplicates().tolist() + self.df['to'].drop_duplicates().tolist())        

        return edge_df, vertices
    
    def centraility_with_nx(self, inverse=False, normalize=True, type='pagerank'):
        df_tmp = self.df[['from', 'to', 'count']]
        if inverse:
            df_tmp.rename(columns={'from': 'to', 'to':'from'}, inplace=True)
        if normalize:
            df_tmp['count'] = df_tmp.apply(lambda x: x[2] / self.deg_out[x[0]] if not inverse else x[2] / self.deg_in[x[1]], axis=1)
        G = nx.DiGraph()
        G.add_weighted_edges_from(df_tmp[['from', 'to', 'count']].values.tolist())
        if type == 'pagerank':
            place_cent = nx.pagerank(G)
        elif type == 'closeness':
            place_cent = nx.closeness_centrality(G)
        elif type == 'betweeness':
            place_cent = nx.betweenness_centrality(G)
        elif type == 'hits':
            place_cent = nx.hits(G, max_iter=1000)
        if type != 'hits':
            ret = [0] * len(self.places)
            for place, val in place_cent.items():
                ret[int(place)] = val
            return ret
        else:
            ret_hub, ret_auth = [0] * len(self.places), [0] * len(self.places)
            for place, val in place_cent[0].items():
                ret_hub[int(place)] = val
            for place, val in place_cent[1].items():
                ret_auth[int(place)] = val
            return ret_hub, ret_auth

    def calc_centrality(self, pr_hits=True):
        df = pd.DataFrame()
        df['name'] = self.places

        df['flow_in'] = self.deg_in
        df['flow_out'] =  self.deg_out
        df['flow_in_net'] = [fin - fout for fin, fout in zip(self.deg_in, self.deg_out)]
        df['flow_out_net'] = [fout - fin for fin, fout in zip(self.deg_in, self.deg_out)]

        if pr_hits:
            df['pr'] = self.centraility_with_nx(inverse=False, normalize=False, type='pagerank')
            df['pr_norm'] = self.centraility_with_nx(inverse=False, normalize=True, type='pagerank')
            df['pr_norm_inv'] = self.centraility_with_nx(inverse=True, normalize=True, type='pagerank')
            df['pr_inv'] = self.centraility_with_nx(inverse=True, normalize=False, type='pagerank')

            hubs, auths = self.centraility_with_nx(inverse=False, normalize=False, type='hits')
            df['hub'] = hubs
            df['authority'] = auths
            hubs, auths = self.centraility_with_nx(inverse=False, normalize=True, type='hits')
            df['hub_norm'] = hubs
            df['authority_norm'] = auths

        return df

    def calc_cluster_lovain(self, normalize=False, resolution=1, init_cls={}):
        df_tmp = self.df[['from', 'to', 'count']]
        if normalize:
            df_tmp['count'] = df_tmp.apply(lambda x: x[2] / self.deg_out[x[0]], axis=1)

        df_inverse = df_tmp.rename(columns={'from': 'to', 'to': 'from'}, inplace=False)
        df_tmp = df_tmp.append(df_inverse)
        df_tmp = df_tmp.groupby(['from', 'to']).sum().reset_index()
        df_tmp = df_tmp[df_tmp[['from', 'to']].apply(lambda x: x[0] < x[1], axis=1)]
        
        G = nx.Graph()
        G.add_weighted_edges_from(df_tmp[['from', 'to', 'count']].values.tolist())
        if len(init_cls) != 0:
            partition = community_louvain.best_partition(G, resolution=resolution, partition=init_cls)
        else:
            partition = community_louvain.best_partition(G, resolution=resolution)
        labels = [0] * len(partition)
        for key, val in partition.items():
            labels[int(key)] = val
        return labels
