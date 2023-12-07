# -*- coding: utf-8 -*-
import sys

sys.path.append('/code')
sys.path.append('/code/Site')

import pickle
from collections import defaultdict
# from tqdm import tqdm
import cPickle
# from CONFIG import DATA_PATH

reload(sys)
sys.setdefaultencoding('utf-8')

class Node(object):
    def __init__(self, ch='', idx=-1, depth=0, is_root=False, parent=None):
        self._next_p = {} # {字符: 节点编号}
        self.fail = 0
        self.is_root = is_root
        self.ch = ch
        self.parent = parent
        self.idx = idx
        self.depth = depth

    def __iter__(self):
        return iter(self._next_p.keys())

    def __getitem__(self, item):
        return self._next_p[item]

    def __setitem__(self, key, value):
        _u = self._next_p.setdefault(key, value)


def node_append(root, nodes, _node_meta, keyword, tmp_dct):
    assert len(keyword) > 0
    u = root
    node = nodes[u]
    for idx, ch in enumerate(keyword): # idx记录节点深度
        # 没有节点的话新建一个
        if ch not in node:
            nodes.append(Node(ch, depth=idx + 1, idx=len(nodes), parent=u))
            node[ch] = len(nodes) - 1
        
        u_nxt = node[ch]
        if idx >=1: 
            for _j in tmp_dct[ch]: # 每个包含ch的词
                if keyword[:idx + 1].endswith(_j): 
                    _node_meta[u_nxt].add((_j, len(_j)))
        u = u_nxt
        node = nodes[u]
    else:
        if u != root:
            _node_meta[u].add((keyword, len(keyword)))

def init_AC(*words):
    root = 0 
    nodes = [Node(is_root=True, idx=0, depth=0)]  # 深度，节点
    _node_meta = defaultdict(set)

    tmp_dct = {}
    for word in words:
        for w in word:
            tmp_dct.setdefault(w, set())
            tmp_dct[w].add(word)
    words_set = set(words)
    words = list(words_set)
    words.sort(key=lambda x: len(x))
    for word in words:
        node_append(root, nodes, _node_meta, word, tmp_dct)
    return root, nodes, _node_meta

def make_fail(root, nodes):
    sorted_nodes = sorted(nodes, key=lambda x: x.depth)
    for node in sorted_nodes:
        if node.idx == root or node.depth <= 1:
            node.fail = root
        else:
            next_u = nodes[node.parent].fail
            while True:
                if node.ch in nodes[next_u]:
                    node.fail = nodes[next_u][node.ch]
                    break
                elif next_u == root:
                    node.fail = root
                    break
                else:
                    next_u = node.fail

def search(content, root, nodes, _node_meta, with_index=False):
    result = set()
    u = root
    index = 0
    for i in content:
        while 1:
            if i not in nodes[u]:
                if u == root:
                    break
                else:
                    u = nodes[u].fail
            else:
                for keyword, keyword_len in _node_meta.get(nodes[u][i], set()):
                    if not with_index:
                        result.add(keyword)
                    else:
                        result.add((keyword, (index - keyword_len + 1, index + 1)))
                u = nodes[u][i]
                break
        index += 1
    return result


def distance(loc1, loc2):
    return (loc1[0] - loc2[0]) * (loc1[0] - loc2[0]) + (loc1[1] - loc2[1]) * (loc1[1] - loc2[1])


def init_matcher(filepath, coarse_bottom='region'):
    coarse_dct = {'province': 0, 'city': 1, 'region': 2}
    coarse_level = coarse_dct[coarse_bottom]
    with open(filepath, 'rb') as f:
        dct_all = pickle.load(f)
    word_dct = {}
    for key, lst in dct_all.items():  # word, (province, city, region, (type, loc_dict[province]))
        word_dct[key] = []
        for ele in lst:
            if ele[-1][0] <= coarse_level:
                word_dct[key].append(ele)
    words_all = word_dct.keys()

    # 观察keyword有没有覆盖的
    dict_coverage = {}
    for keyword1 in words_all:
        for keyword2 in words_all:
            if keyword1 != keyword2 and keyword1.find(keyword2) != -1:
                if keyword1 not in dict_coverage:
                    dict_coverage[keyword1] = []
                dict_coverage[keyword1].append(keyword2)
    root, nodes, _node_meta = init_AC(*[u.encode('utf-8') for u in words_all])
    make_fail(root, nodes)
    return root, nodes, _node_meta, dict_coverage, word_dct
    

def find_keykeywords(root, nodes, _node_meta, dict_coverage, query):
    lst = []
    for word in search(query, root, nodes, _node_meta):
        lst.append(word)
    match_set = set(lst)
    for keyword, sub_keywords in dict_coverage.items():
        if keyword in match_set:
            for keyword_sub in sub_keywords:
                match_set.discard(keyword_sub)
    return [u.decode('utf-8') for u in match_set]
    
def judge_cover(place, place_large):
    # 判断place被place_large覆盖
    for ele1, ele2 in zip(place[:3], place_large[:3]):
        if ele1 != ele2 and ele2 != 'NuLL':
            return False
    return True

def match_query(root, nodes, _node_meta, dict_coverage, word_dct, query, location, province): # 返回一个最匹配的位置
    # [(province_now, city_now, region_now, (priority, province_location, ori_priority), ...]
    keywords = find_keykeywords(root, nodes, _node_meta, dict_coverage, query) # [word1, word2, word3]
    candidates_tmp = []
    for keyword in keywords:
        candidates_tmp.extend(word_dct[keyword])
    candidates = []

    if len(candidates_tmp) == 0:
        return None

    # 匹配到的有没有覆盖的
    candidates_nocover = []
    for u, ele in enumerate(candidates_tmp):
        cover_flag = False        
        for k, ele_other in enumerate(candidates_tmp):
            if k == u:
                continue
            if judge_cover(ele_other, ele): # 覆盖了更小区域，删掉这个匹配，提高小区域优先级
                cover_flag = True
                ele_other[-1][0] = min(ele[-1][0], ele_other[-1][0])
        if not cover_flag:
            candidates_nocover.append(ele)
    candidates_tmp = candidates_nocover

    # 是否省内搜索
    for ele in candidates_tmp:
        if ele[0] == province:
            candidates.append(ele)

    if len(candidates) > 1:
        candiates_tmp = candidates
        candidates = []

    if len(candidates) == 0:    # 不是省内搜索，或省内搜索有多个
        # 优先级: 优先省, 优先市，最后才是区
        max_level = min([u[-1][0] for u in candidates_tmp])
        for ele in candidates_tmp:
            if ele[-1][0] == max_level:
                candidates.append(ele)

    # 没有匹配到
    if len(candidates) == 0:
        return None

    # 同cover级别，过滤ori_level小的
    candidates_tmp = []        
    max_level = min([u[-1][2] for u in candidates])
    for ele in candidates:
        if ele[-1][2] == max_level:
            candidates_tmp.append(ele)
    candidates = candidates_tmp


    # 同级别找最近的
    ret = candidates[0]
    dis_min = distance(ret[-1][1], location)
    for ele in candidates:
        dis_now = distance(ele[-1][1], location)
        if dis_now < dis_min:
            dis_min = dis_now
            ret = ele
    
    return ret[:-1]  # (province_now, city_now, region_now)

def print_lst(lst):
    for a in lst:
        print a,
    print('')

if __name__ == "__main__":
    root, nodes, _node_meta, dict_coverage, word_dct = init_matcher("%s/city/area_dict.pkl" % DATA_PATH, coarse_bottom='region')
    # print(find_keykeywords(root, nodes, _node_meta, dict_coverage, '欢迎来到吉林'))
    # ac = ACAutomaton('a', 'ab', 'bc', 'abc', 'bcd')
    # print(ac.search('abcd'))
    # print(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '浙江省杭州市', [126.534137, 45.811235], '黑龙江省'))

    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '浙江省杭州市', [126.534137, 45.811235], '黑龙江省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '吉林', [126.534137, 45.811235], '上海市'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '绍兴社区工作者招聘;;2020年浙江省社区工作者考试公告/大纲_浙江省社区考试', [126.534137, 45.811235], '上海市'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '2019浙江嘉兴学院招聘15人公告;;2019浙江嘉兴学院招聘15人公告-事业单位招聘考试网', [126.534137, 45.811235], '上海市'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '温岭人才招聘网;;温岭人才网-温岭人才交流中心唯一官方网站|浙江人才网', [126.534137, 45.811235], '上海市'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '东海县医院招聘', [126.534137, 45.811235], '上海市'))
    # # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '找工作的合作司机;;\"\"', [101.773523, 36.625934], '青海省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '四川罗江金山招聘;;罗江县金山中心卫生院招聘招聘罗江县金山中心卫生院招聘信息-58...', [101.773523, 36.625934], '青海省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '泰山瑞豹招聘;;德州质检员招聘信息|山东泰山瑞豹复合材料有限公司招聘信息-齐鲁人才', [101.773523, 36.625934], '青海省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '吉林省双辽市找工作保洁;;\"\"', [101.773523, 36.625934], '青海省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '兴国人才网最新招聘信息网;;\"\"', [101.773523, 36.625934], '江西省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '江西省兴国县招聘信息;;\"\"', [101.773523, 36.625934], '江西省'))
    
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '张家口市桥东找工作', [114.889699,40.776516], '河北省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '贵阳市白云区计划招聘教师266人、保育员136人!;;2020贵阳白云区计划招聘教师266人保育员136人!-师迅宝教师', [11557837.708634032, 2918380.2754198536], '云南省'))
    # print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '徐工集团招聘组装;;徐工集团招聘装配工普工5000以上长白班-徐州鼓楼金山', [13034138.488165058, 4303926.287801762], '山东省'))
    print_lst(match_query(root, nodes, _node_meta, dict_coverage, word_dct, '南方医院太和分院招聘;;南方医院太和分院最新招聘职位_丁香人才网', [12613205.509024294, 2636651.5744090592], '广东省'))
    