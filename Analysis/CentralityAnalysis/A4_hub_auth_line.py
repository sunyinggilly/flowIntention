import sys
sys.path.append('/code')
import pandas as pd
import numpy as np
from CONFIG import *
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
from Utils.util_read import read_translation
from Utils.tools import make_path
plt.switch_backend('agg')


dct_translation = read_translation()

def get_rank(df_c, centrality, time):
    df = df_c[df_c['time'] == time]
    df = df[['name', centrality]]
    df = df.sort_values(by=centrality, ascending=False).head(100)
    df['rank'] = [i + 1 for i in range(df.shape[0])]
    df[centrality] = df[centrality].apply(lambda x: round(x, 4))
    df_now = df[['name', centrality]]
    df_now['name'] = df_now['name'].apply(lambda x: dct_translation[x])
    df_now.rename(columns={'name': 'name_%s' % time, centrality: '%s_%s' % (centrality, time)}, inplace=True)
    return df_now.reset_index(drop=True)

if __name__ == "__main__":
    graph_name = sys.argv[1]
    make_path(OUT_CENTRALITY_PATH)
    df_centrality = pd.read_csv("%s/%s/centrality/city_centrality.csv" % (ANA_DATA_PATH, graph_name))
    time_list = df_centrality['time'].sort_values(ascending=True)
    
    cities = ['北京市', '上海市', '深圳市', '广州市', '苏州市', '杭州市']
    df_now = df_centrality[df_centrality['name'].isin(cities)]
    df_now = df_now.rename(columns={'name': 'city'}, inplace=False)
    df_now['City'] = df_now['city'].apply(lambda x: dct_translation[x])

    df_now['Period'] = df_now['time']
    df_now['Authority'] = df_now['authority']
    df_now['Hub'] = df_now['hub']
    
    if graph_name == 'month':
        df_now['Period'] = pd.to_datetime(df_now['Period'].astype(str), format='%Y%m')

    lineplt = sns.lineplot(data=df_now, hue='City', x='Period', y='Authority')
    sns.scatterplot(data=df_now, hue='City', y='Authority', x='Period', s=50, legend=False)
    plt.xticks(rotation=30) 
    lineplt.legend(loc='best', ncol=3, fancybox=True)
    plt.savefig('%s/auth_city_line_%s.png' % (OUT_CENTRALITY_PATH, graph_name))
    plt.close()
    lineplt = sns.lineplot(data=df_now, hue='City', x='Period', y='Hub')
    sns.scatterplot(data=df_now, hue='City', y='Hub', x='Period', s=50, legend=False)
    plt.xticks(rotation=30) 
    lineplt.legend(loc='best', ncol=3, fancybox=True)
    plt.savefig('%s/hub_city_line_%s.png' % (OUT_CENTRALITY_PATH, graph_name))
    plt.close()
