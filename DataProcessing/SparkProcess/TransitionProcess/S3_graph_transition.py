# -*- coding: utf-8 -*-
import pandas as pd
import jieba
import sys
from pyspark import *
from pyspark.sql import *
from datetime import datetime
import pickle
import codecs
import shlex
# from AreaMatcher_NS import AreaMatcher
from AreaMatcher import init_matcher, match_query

reload(sys)
sys.setdefaultencoding('utf-8')

HOME_PATH = "/home/tic_intern/sunying10/works/RFLOW"
DATA_PATH = "%s/Data" % HOME_PATH
TRANS_PATH = "%s/transition" % DATA_PATH

def connect_spark():
    conf = SparkConf()
    conf = conf.setAppName('graph_transition')
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    spark = SparkSession \
        .builder \
        .appName("query_process") \
        .config("spark.some.config.option", "some-value") \
        .enableHiveSupport() \
        .getOrCreate()
    return sc, spark

def generate_graph(rdd):
    rdd = rdd.map(lambda x: (x[0], '-'.join(x[1: 4]), x[5], x[6], x[7], x[8])).distinct()
    rdd = rdd.map(lambda x: ((x[1], x[2], x[3], x[4], x[5]), 1)).reduceByKey(lambda a, b: a + b)
    rdd = rdd.map(lambda x: (x[0][0], x[0][1], x[0][2], x[0][3], x[0][4], x[1]))
    data = rdd.collect()
    df = pd.DataFrame(data, columns=['time', 'province_from', 'city_from', 'province_to', 'city_to', 'count'])
    return df

if __name__ == "__main__":
    timestr = sys.argv[1]
    sc, spark = connect_spark()
    # userid, year, month, day, hour, province_from, city_from, province_to, city_to
    rdd = sc.textFile('/user/bpit_afs/tic/users/sunying10/job_query2/trans-%s' % timestr).map(lambda x: x.encode('utf-8').split(',')).repartition(300)
    df = generate_graph(rdd)
    df.to_csv("%s/%s.csv" % (TRANS_PATH, timestr), index=False)

# event_query, event_time, event_province, event_city, event_userid,
# event_click_target_url, event_click_target_title, wiseps_query_level1_type, wiseps_query_level2_type,
# event_ip, event_useragent, event_isinternalip, event_phonenum, wiseps_phonetype, wiseps_isp, wiseps_access, 
# event_os, event_browser, regexp_extract(event_cookie,'(.*?)BAIDULOC=(.*?)(\;.*|$)',2) as location_cookie
