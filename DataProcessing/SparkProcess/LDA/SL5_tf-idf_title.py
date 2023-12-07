# -*- coding: utf-8 -*-
import pandas as pd
import sys
from pyspark import *
from pyspark.sql import *
from datetime import datetime
from pyspark.mllib.linalg import SparseVector
from pyspark.mllib.clustering import GaussianMixture, KMeans, KMeansModel
import pickle
import codecs
from numpy import array
import re
import pandas as pd
import jieba
import random
reload(sys)
sys.setdefaultencoding('utf-8')
HOME_PATH = "/home/tic_intern/sunying10/works/RFLOW"
FLOW_DATA_PATH = "%s/Data/FlowData" % HOME_PATH
NTM_DATA_PATH = "%s/Data/NTMData" % HOME_PATH

def map_city(x):
    if x in ['海西蒙古族藏族自治州', '玉树藏族自治州', '博尔塔拉蒙古自治州', '黔西南布依族苗族自治州', '克孜勒苏柯尔克孜自治州', '喀什地区', '塔城地区',
             '和田地区', '昌吉回族自治州', '阿勒泰地区', '果洛藏族自治州', '德宏傣族景颇族自治州', '甘南藏族自治州', '甘孜藏族自治州', '红河哈尼族彝族自治州', 
             '海南藏族自治州', '阿坝藏族羌族自治州', '阿克苏地区', '黔东南苗族侗族自治州', '延边朝鲜族自治州', '迪庆藏族自治州', '西双版纳傣族自治州', '大兴安岭地区', '黔南布依族苗族自治州', 
             '阿里地区', '楚雄彝族自治州', '文山壮族苗族自治州', '大理白族自治州', '黄南藏族自治州', '巴音郭楞蒙古自治州', '临夏回族自治州', '海北藏族自治州', 
             '湘西土家族苗族自治州', '伊犁哈萨克自治州', '怒江傈僳族自治州', '凉山彝族自治州']:
        return x
    dct = {'迪庆':'迪庆藏族自治州', '临夏':'临夏回族自治州', '黔南':'黔南布依族苗族自治州', '和田':'和田地区', 
           '甘孜':'甘孜藏族自治州', '黔东南':'黔东南苗族侗族自治州', '阿勒泰':'阿勒泰地区', '大理':'大理白族自治州', '吐鲁番地区': '吐鲁番市',
           '楚雄':'楚雄彝族自治州', '怒江':'怒江傈僳族自治州', '香港':'香港特别行政区', '澳门':'澳门特别行政区', '林芝地区': '林芝市', '那曲地区': '那曲市',
           '锡林郭勒盟':'锡林郭勒盟', '博尔塔拉':'博尔塔拉蒙古自治州', '甘南':'甘南藏族自治州', '黔西南':'黔西南布依族苗族自治州', 
           '湘西':'湘西土家族苗族自治州', '阿克苏':'阿克苏地区', '塔城':'塔城地区', '阿里':'阿里地区', '延边':'延边朝鲜族自治州', 
           '大兴安岭':'大兴安岭地区', '文山':'文山壮族苗族自治州', '喀什':'喀什地区', '果洛':'果洛藏族自治州', 
           '阿坝':'阿坝藏族羌族自治州', '恩施':'恩施土家族苗族自治州', '恩施州': '恩施土家族苗族自治州', '巴音郭楞':'巴音郭楞蒙古自治州', 
           '凉山':'凉山彝族自治州', '阿拉善盟':'阿拉善盟', '黄南':'黄南藏族自治州', '红河':'红河哈尼族彝族自治州', '山南地区': '山南市', 
           '海南':'乌海市', '海北':'海北藏族自治州', '玉树':'玉树藏族自治州', '西双版纳':'西双版纳傣族自治州', '昌吉':'昌吉回族自治州', 
           '兴安盟':'兴安盟', '海西':'海西蒙古族藏族自治州', '德宏':'德宏傣族景颇族自治州', '莱芜':'济南市', '伊犁':'伊犁哈萨克自治州',
           '澄迈县': '澄迈县', '白沙黎族自治县':'白沙黎族自治县', '临高县':'临高县', '乐东黎族自治县': '乐东黎族自治县', '哈密地区': '哈密市', 
           '定安县':'定安县', '昌江黎族自治县':'昌江黎族自治县', '琼中黎族苗族自治县':'琼中黎族苗族自治县', '襄樊':'襄阳市', 
           '神农架':'神农架林区', '克孜勒苏柯尔克孜':'克孜勒苏柯尔克孜自治州', '屯昌县':'屯昌县', '昌都地区': '昌都市',
           '保亭黎族苗族自治县':'保亭黎族苗族自治县', '陵水黎族自治县': '陵水黎族自治县'}
    if x in ['鹤岗', '鹰潭', '三门峡', '韶关', '六安', '南宁', '上饶', '牡丹江', '十堰', '张家界', '自贡', '商洛', '贵阳',
             '无锡', '中卫', '杭州', '万宁', '吉林', '龙岩', '济南', '连云港', '伊春', '枣庄', '遵义', '内江', '遂宁', 
             '黄冈', '丹东', '双鸭山', '武汉', '东营', '常州', '巴中', '四平', '昆明', '平顶山', '荆州', '亳州', '宜春', 
             '潮州', '临沧', '昌都', '安阳', '运城', '哈密', '西安', '襄阳', '绍兴', '苏州', '南京', '普洱', '岳阳', 
             '宜宾', '六盘水', '黑河', '九江', '景德镇', '泉州', '娄底', '盘锦', '西宁', '石嘴山', '成都', '本溪', 
             '清远', '中山', '海口', '眉山', '平凉', '桂林', '乌兰察布', '莆田', '上海', '盐城', '金昌', '防城港', 
             '淄博', '石家庄', '宜昌', '河池', '保定', '河源', '昭通', '赣州', '辽源', '图木舒克', '宣城', '泰州', 
             '琼海', '五家渠', '廊坊', '太原', '乌鲁木齐', '台州', '惠州', '汕尾', '辽阳', '齐齐哈尔', '北海', '许昌', 
             '淮安', '茂名', '南平', '广元', '荆门', '定西', '唐山', '漯河', '那曲', '鞍山', '仙桃', '忻州', '黄山', 
             '潜江', '包头', '吉安', '德阳', '嘉兴', '铜陵', '绵阳', '青岛', '济源', '怀化', '三亚', '南充', '宿迁', 
             '濮阳', '雅安', '安顺', '开封', '徐州', '锦州', '邯郸', '驻马店', '丽江', '柳州', '陇南', '沧州', '梧州', 
             '玉林', '营口', '阳泉', '嘉峪关', '萍乡', '石河子', '林芝', '肇庆', '滨州', '晋中', '呼伦贝尔', '延安', '钦州', 
             '东方', '淮南', '信阳', '葫芦岛', '鄂州', '崇左', '鹤壁', '泰安', '东莞', '阳江', '随州', '蚌埠', '温州', '兰州', 
             '朔州', '黄石', '白银', '镇江', '抚顺', '安康', '金华', '日照', '长沙', '宝鸡', '烟台', '咸宁', '大庆', '大同', 
             '焦作', '鸡西', '南通', '衢州', '南阳', '海东', '承德', '重庆', '泸州', '曲靖', '乌海', '济宁', '晋城', '玉溪', 
             '佛山', '鄂尔多斯', '深圳', '池州', '威海', '厦门', '七台河', '安庆', '天津', '衡水', '巴彦淖尔', '儋州', '衡阳', 
             '芜湖', '五指山', '绥化', '乐山', '宁波', '邵阳', '铜仁', '汕头', '三明', '菏泽', '株洲', '渭南', '广州', '沈阳', 
             '江门', '德州', '银川', '白山', '日喀则', '张掖', '梅州', '阿拉尔', '舟山', '郴州', '达州', '酒泉', '湘潭', 
             '长治', '周口', '攀枝花', '吕梁', '云浮', '阜新', '吴忠', '抚州', '天门', '扬州', '淮北', '百色', '文昌', '资阳', 
             '永州', '松原', '庆阳', '洛阳', '咸阳', '朝阳', '长春', '揭阳', '秦皇岛', '铁岭', '佳木斯', '天水', '毕节', '汉中', 
             '南昌', '郑州', '张家口', '拉萨', '哈尔滨', '邢台', '珠海', '北京', '山南', '滁州', '商丘', '来宾', '赤峰', '贵港', 
             '新乡', '漳州', '新余', '吐鲁番', '常德', '大连', '阜阳', '益阳', '宿州', '合肥', '广安', '铜川', '固原', 
             '呼和浩特', '克拉玛依', '通辽', '湖州', '聊城', '丽水', '白城', '保山', '临汾', '湛江', '潍坊', '孝感', '榆林', 
             '武威', '临沂', '宁德', '福州', '马鞍山', '贺州', '通化']:
        return x + '市'
    if x in dct:
        return dct[x]
    else:
        return None


def map_province(x): 
    if x in ['青海', '甘肃', '云南', '湖北', '海南', '浙江', '吉林', '贵州', '江苏', '山东', '安徽', '台湾', 
             '山西', '福建', '广东', '江西', '辽宁', '黑龙江', '河北', '河南', '湖南', '陕西', '四川']: 
        return x + '省'
    if x in ['北京','上海','重庆','天津']:
        return x + '市'
    if x in ['内蒙古', '西藏']: # 内蒙古, 西藏
        return x + '自治区'
    if x == '宁夏':
        return '宁夏回族自治区'
    if x == '新疆':
        return '新疆维吾尔自治区'
    if x == '广西':
        return '广西壮族自治区'
    if x in ['香港', '澳门']:
        return x + '特别行政区'
    return None


def connect_spark():
    conf = SparkConf()
    conf = conf.setAppName('SYem')
    sc = SparkContext(conf=conf)
    # sc.setLogLevel("ERROR")
    spark = SparkSession \
        .builder \
        .appName("SYem") \
        .config("spark.some.config.option", "some-value") \
        .enableHiveSupport() \
        .getOrCreate()
    return sc, spark

def find_keywords(x, keywords):
    lst = []
    for u, word in enumerate(keywords):
        if x.find(word) != -1:
            lst.append(u)
    return lst

def sparse_to_dense(x, n):
    ret = [0] * n
    for u, v in x:
        ret[u] += v
    return ret


def read_dct():
    words = pd.read_csv("out/word_idf_title.csv").values.tolist()
    # words = pd.read_csv("out/word_idf_origin.csv").values.tolist()
    id2word = []
    word_idf = []
    dct = {}
    for u, w_c in enumerate(words):
        word, count = w_c
        word = word.decode('utf-8')
        dct[word] = u
        id2word.append(word)
        word_idf.append(count)
        
    return dct, id2word, word_idf


def txt2vec(x, word_dct, word_idf, norm=False):
    tf = {}
    all_sum = 0 # 总数
    for u in jieba.cut(x):  #.encode('utf-8')
        if u in word_dct:
            u = word_dct[u]
            tf[u] = (tf[u] + 1.0) if u in tf else 1.0
            # tf[u] = 1
        all_sum += 1
    tfidf_sum = 0
    for key, _ in tf.items():
        tf[key] = tf[key] / all_sum # * word_idf[key]
        # tf[key] = tf[key] / all_sum * word_idf[key]
        tfidf_sum += tf[key]
    if norm:
        for key, _ in tf.items():
            tf[key] = tf[key] / tfidf_sum
    return SparseVector(len(word_dct), tf)


def gmm_clustering(rdd, K):
    gmm = GaussianMixture() #.setK(K).setSeed(538009335)
    model = gmm.train(rdd, K)
    for i in range(K):
        print("weight = ", gmm.weights[i], "mu = ", gmm.gaussians[i].mu,
            "sigma = ", gmm.gaussians[i].sigma.toArray())
    return model

def kmeans_clustering(rdd, K):
    model = KMeans.train(rdd, K)
    # print(model.clusterCenters)
    # for i in range(K):
    #     print("weight = ", gmm.weights[i], "mu = ", gmm.gaussians[i].mu,
    #         "sigma = ", gmm.gaussians[i].sigma.toArray())
    return model, model.clusterCenters

# 还要求一下idf，之前算的是错的：log(总文件数/每个词出现的文件数) 单开一个py文件吧
if __name__ == "__main__":
    K = 30
    word_dct, word_lst, word_idf = read_dct()

    sc, spark = connect_spark()
    sql_fetch = "SELECT city, startdate, title FROM tic_dw.dwd_bp_job_post WHERE startdate like concat('2019-1', '%') or startdate like concat('2020', '%') or startdate like concat('2021', '%')"
    rdd = spark.sql(sql_fetch).rdd
    # rdd = rdd.filter(lambda x: random.random() < 0.01) # 先取 1%测试

    # sql_fetch = "SELECT city, startdate, description FROM tic_dw.dwd_bp_job_post WHERE startdate like concat('2019-11', '%')"
    # rdd = spark.sql(sql_fetch).rdd
    
    rdd = rdd.filter(lambda x: x[0] is not None and x[1] is not None and x[2] is not None)
    rdd = rdd.map(lambda x: (map_city(x[0].encode('utf-8')), int(x[1].replace('-', '')[:6]), txt2vec(x[2], word_dct, word_idf, norm=True))) # city, date, bag(sparseVector)
    rdd = rdd.filter(lambda x: x[0] is not None)
    rdd_vecs = rdd.map(lambda x: x[-1]) # sparseVector
    
    # ------------------------ gmm ----------------------------------------
    # gmm_model = gmm_clustering(rdd_vecs, K)
    # rdd = rdd.map(lambda x: ((x[0], x[1]), gmm_model.predictSoft(x[2])))
    # rdd = rdd.reduceByKey(lambda a, b: [u + v for u, v in zip(a, b)])
    # rdd = rdd.map(lambda x: ([x[0][0], x[0][1]] + x[1]))
    # data = rdd.collect()
    # df = pd.DataFrame(data, columns=['city', 'time', 'topic'] + ['K%d' % u for u in range(K)])
    
    kmeans_model, topic_word_dis = kmeans_clustering(rdd_vecs, K)
    rdd = rdd.map(lambda x: ((x[0], x[1], kmeans_model.predict(x[2])), 1))
    rdd = rdd.reduceByKey(lambda a, b: a + b)
    rdd = rdd.map(lambda x: (x[0][0], x[0][1], x[0][2], x[1]))
    data = rdd.collect()
    df = pd.DataFrame(data, columns=['city', 'time', 'topic', 'count'])
    df.to_csv("out/city_topic.csv", index=False)

    df_topic_word = pd.DataFrame()
    df_topic_word['word'] = word_lst
    for T, p_lst in enumerate(topic_word_dis):
        df_topic_word["K%d" % T] = p_lst
    df_topic_word.to_csv("out/topic_word.csv", index=False)



###### 这应该是最终版本
