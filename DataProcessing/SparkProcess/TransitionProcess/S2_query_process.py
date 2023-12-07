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
from AreaMatcher import init_matcher, match_query
import random

reload(sys)
sys.setdefaultencoding('utf-8')

HOME_PATH = "/home/tic_intern/sunying10/works/RFLOW"
DATA_PATH = "%s/Data" % HOME_PATH
TRANS_PATH = "%s/transition" % DATA_PATH
CITY_DATA_PATH = "%s/city" % DATA_PATH


def connect_spark():
    conf = SparkConf()
    conf = conf.setAppName('query_process')
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    spark = SparkSession \
        .builder \
        .appName("query_process") \
        .config("spark.some.config.option", "some-value") \
        .enableHiveSupport() \
        .getOrCreate()
    return sc, spark


def process_location(x):
    loc_x, loc_y = x[1:-1].split(',')
    return [float(loc_x), float(loc_y)]


def get_grid_id(x, y, grid_len):
    x = int(x) // grid_len
    y = int(y) // grid_len
    return x * 100000 + y


# 3d试机号,17A3A7242614647D024943F1D073E98F|179759730770068,(11600243.0, 3654661.0),,,BB7E5D4F4591A11067EAC5E491EE1ADE,0,,android,,绵阳,四川,117.136.82.196,20191215181826,4g
def fetch_cols(x, locatation2city, id2city, grid_len):
    try:
        event_time = datetime(int(x[13][:4]), int(x[13][4:6]), int(x[13][6:8]), 
                              int(x[13][8:10]), int(x[13][10:12]), int(x[13][12:14]))
        loc = process_location(x[2])
        loc = (int(loc[0]), int(loc[1]))
    except:
        return [None, None, None, None, None, None]

    gid = get_grid_id(loc[0], loc[1], grid_len)
    if gid in locatation2city:
        place_frm = locatation2city[gid]
        province, city = id2city[place_frm]
        return [(x[0], x[4]), event_time, province.encode('utf-8'), city.encode('utf-8'), x[5], process_location(x[2])]
    return [None, None, None, None, None, None]


def query_locate(x, nodes, _node_meta, dict_coverage, word_dct):
    # (event_query, event_click_target_title), event_time, province, city, event_userid, location
    query = (x[0][0] + ';;' + x[0][1]).replace(',', ' ')
    target = match_query(root, nodes, _node_meta, dict_coverage, word_dct, query, x[-1], x[2])
    return (target[0], target[1], target[2]) if target is not None else None, (x[1].year, x[1].month, x[1].day, x[1].hour), x[2], x[3], x[4], query
    # destination, event_time, event_province, event_city, event_userid


if __name__ == "__main__":
    grid_len = 2000
    timestr = sys.argv[1]

    with open('%s/city/location2city.pkl' % DATA_PATH, 'rb') as f:
        locatation2city_dct, id2city = pickle.load(f) 

    root, nodes, _node_meta, dict_coverage, word_dct = init_matcher("%s/area_dict.pkl" % CITY_DATA_PATH, coarse_bottom='region')

    sc, spark = connect_spark()
    locatation2city_dct_b = sc.broadcast(locatation2city_dct)
    
    rdd = sc.textFile("/user/bpit_afs/tic/users/sunying10/Query/%s/**" % timestr)
    rdd = rdd.map(lambda x: x.encode('utf-8').split('\t'))
    rdd = rdd.filter(lambda x: (x[0].find('招聘') != -1 or x[0].find('求职') != -1 or x[0].find('找工作') != -1))
    
    rdd = rdd.map(lambda x: fetch_cols(x, locatation2city_dct_b.value, id2city, grid_len))
    rdd = rdd.filter(lambda x: x[2] is not None and x[3] is not None and x[-1] is not None)

    # destination, event_time, event_province, event_city, event_userid
    rdd = rdd.map(lambda x: query_locate(x, nodes, _node_meta, dict_coverage, word_dct))
    rdd = rdd.filter(lambda x: x[0] is not None)
    rdd = rdd.distinct() 

    # userid, year, month, day, hour, province_from, city_from, province_to, city_to
    rdd = rdd.map(lambda x: (x[4], x[1][0], x[1][1], x[1][2], x[1][3], x[2].decode('utf-8'), x[3].decode('utf-8'), x[0][0], x[0][1], x[-1].decode('utf-8'))) 
    df = spark.createDataFrame(rdd, ['userid', 'year', 'month', 'day', 'hour', 'province_from', 'city_from', 'province_to', 'city_to', 'query'])
    df.repartition(100).write.csv('/user/bpit_afs/tic/users/sunying10/job_query2/trans-%s' % timestr)
    locatation2city_dct_b.unpersist 
