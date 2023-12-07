import sys
sys.path.append('/code')
import networkx as nx
import pandas as pd
from CONFIG import ANA_DATA_PATH
from Utils.tools import make_path
from tqdm import tqdm
from Utils.util_read import read_graph


if __name__ == "__main__":
    make_path("%s/month/graph/" % ANA_DATA_PATH)
    make_path("%s/season/graph/" % ANA_DATA_PATH)
    make_path("%s/all/graph/" % ANA_DATA_PATH)

    df_province = read_graph(coarse_time='month', coarse='province', time_from=(2019, 10), time_end=(2022, 12), self_edge=True)
    df_city = read_graph(coarse_time='month', coarse='city', time_from=(2019, 10), time_end=(2022, 12), self_edge=True)
    df_province.to_csv("%s/month/graph/province.csv" % ANA_DATA_PATH, index=False)
    df_city.to_csv("%s/month/graph/city.csv" % ANA_DATA_PATH, index=False)

    df_province = read_graph(coarse_time='season', coarse='province', time_from=(2019, 10), time_end=(2022, 12), self_edge=True)
    df_city = read_graph(coarse_time='season', coarse='city', time_from=(2019, 10), time_end=(2022, 12), self_edge=True)
    df_province.to_csv("%s/season/graph/province.csv" % ANA_DATA_PATH, index=False)
    df_city.to_csv("%s/season/graph/city.csv" % ANA_DATA_PATH, index=False)

    df_province = read_graph(coarse_time='all', coarse='province', time_from=(2019, 10), time_end=(2022, 12), self_edge=True)
    df_city = read_graph(coarse_time='all', coarse='city', time_from=(2019, 10), time_end=(2022, 12), self_edge=True)
    df_province.to_csv("%s/all/graph/province.csv" % ANA_DATA_PATH, index=False)
    df_city.to_csv("%s/all/graph/city.csv" % ANA_DATA_PATH, index=False)
