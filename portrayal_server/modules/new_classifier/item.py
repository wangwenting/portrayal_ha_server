# -*- coding: utf-8 -*-

import os
import json
import logging
import traceback
cur_dir = os.path.dirname(os.path.abspath(__file__))
from industry import Industry
from portrayal_server.zk_config.zk_client import zk_conf

s_key_cat = {}
m_key_cat = []


class multi_key(object):
    def __init__(self, key_str, cat_str):
        self.key = set(key_str.split(u","))
        self.cat = cat_str

    def is_subset(self, words):
        if self.key.issubset(words):
            return self.cat

key_cat_file = cur_dir + "/dict/key_cat.txt"
with open(key_cat_file, "r") as f:
    for line in f:
        try:
            key_str, cat_str = line.strip().decode("u8").split(u"\t")
        except Exception, e:
            logging.info("%s %s", line, e)
            continue
        if key_str.find(u",") != -1:
            mkey = multi_key(key_str, cat_str)
            m_key_cat.append(mkey)
        else:
            s_key_cat[key_str] = cat_str


class Item(object):
    def __init__(self):
        self.cid = u""                   # 商品所属客户的cid
        self.name = u""                  # 商品标题名称
        self.category = u""              # 商品类目，json字符串
        self.brand = u""                 # 商品品牌
        self.price = u""                 # 商品价格
        self.sample = {}                 # 商品的关键词，用于分类
        self.gender = 0                  # 商品性别偏向： {None: 0, male: 1, female: 2}
        self.dest_cat = ""               # 商品目标分类，用"$"符级联
        self.cat_filter = []             # 商品不应分到的类目
        self.flag_classify_done = False  # 分类是否完成的标示

    def load_data(self, cid, name, category, brand, price, sample):
        self.cid = cid
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.sample.update( sample )
        try:
            self.gender = self.get_gender
            self.get_map()
            self.cat_filter = self.get_cat_filter()
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("Item Load Data Error: %s", e)
    
    @property
    def get_gender(self):
        sample_str = u''.join(self.sample.keys())
        flag_M = (sample_str.find(u"男") != -1)
        flag_F = (sample_str.find(u"女") != -1) or (sample_str.find(u'裙') != -1) \
                 or (sample_str.find(u"妇") != -1)
        if flag_M and not flag_F:
            return 1
        elif flag_F and not flag_M:
            return 2
        else:
            return 0

    def get_map(self):
        self.get_cat_map()
        if not self.flag_classify_done:
            dest_cat = self.get_key_map()
            if len(dest_cat) > len(self.dest_cat):
                self.dest_cat = dest_cat
        if not self.dest_cat:
            cat = self.category
            sample_str = u''.join( self.sample.keys() )
            if cat.find(u'儿童') != -1 or cat.find(u'童装') != -1:
                self.dest_cat = u"母婴用品"
            elif sample_str.find(u"手机") != -1 and sample_str.find(u"小米") != -1:
                self.dest_cat = u"手机/手机配件"

    def get_cat_map(self):
        cid = self.cid
        orig_cat = self.category
        try:
            orig_cat_str = u'$'.join(json.loads(orig_cat))
        except Exception, e:
            logging.info("%s\t%s", orig_cat, e)
            orig_cat_str = ""
        config = zk_conf.get_client(cid)
        if not config:
            return
        if "classify_map" in config and bool(config["classify_map"]):
            for cat_map in config["classify_map"]:
                if orig_cat_str.startswith(cat_map["src_category"]):
                    self.dest_cat = cat_map["dst_category"]
                    self.flag_classify_done = (not cat_map["continue_to_classify"])
                    break

    def get_key_map(self):
        words = self.sample.keys()
        for word in words:
            if word in s_key_cat:
                cat_str = s_key_cat[word]
                return cat_str
        for mkey in m_key_cat:
            cat_str = mkey.is_subset(words)
            if cat_str:
                return cat_str
        return u""

    def get_cat_filter(self):
        cid = self.cid
        cat_filter = []
        config = zk_conf.get_client(cid)
        if not config:
            return cat_filter
        if "industry" in config \
            and (config["industry"] == Industry.INDUSTRY_MEDICINE):
            cat_filter = [u"本地生活", u"出差旅游", u"汽车用品", u"服装配饰", \
                          u"运动户外", u"鞋", u"电脑/办公", u"数码", \
                          u"手机/手机配件", u"箱包", u"家具建材", u"珠宝钟表"]
        else:
            pass
        return cat_filter

def test_item():
    cid = u"Ctest"
    name = u"test"
    category = u'["童装"]'
    brand = u"test"
    price = 12.0
    sample = {u"女装": 1}

    print "____gender test____"
    item = Item()
    item.load_data(cid, name, category, brand, price, sample)
    print u"sample: %s\tgender: %s" % (json.dumps(item.sample, ensure_ascii=False), item.get_gender)
    item.sample.update( {u"男性": 1} )
    print u"sample: %s\tgender: %s" % (json.dumps(item.sample, ensure_ascii=False), item.get_gender)

    print "____get_map test____"
    item = Item()
    item.load_data(cid, name, category, brand, price, sample)
    print u"category: %s\tdest_cat: %s\tflag: %s" % \
        (item.category, item.dest_cat, item.flag_classify_done)

    print "____key_map test____"
    item.sample.update( {u"小米": 1, u"手机": 1} )
    item.get_map()
    print u"cid: %s\tsample: %s\tdest_cat: %s\tflag_done: %s" % \
        (cid, json.dumps(item.sample, ensure_ascii=False), item.dest_cat, item.flag_classify_done)
    item.sample = {}

    print "____cat_map test____"
    item.cid = u"C818yiyao"
    item.category = u'["美容护肤"]'
    item.get_map()
    print u"cid: %s\tcategory: %s\tdest_cat: %s\tflag_done: %s" % \
        (item.cid, item.category, item.dest_cat, item.flag_classify_done)
    item.cid = u"Canjuke_haozu"
    item.get_map()
    print u"cid: %s\tcategory: %s\tdest_cat: %s\tflag_done: %s" % \
        (item.cid, item.category, item.dest_cat, item.flag_classify_done)

    print "____cat_filter test____"
    item = Item()
    cid = u"C818yiyao"
    item.load_data(cid, name, category, brand, price, sample)
    print u"cid: %s\tcat_filter: %s" % \
        (item.cid, json.dumps(item.cat_filter, ensure_ascii=False))

def main():
    test_item()

if __name__ == '__main__':
    main()
