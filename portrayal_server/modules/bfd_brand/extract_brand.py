# -*- coding: utf-8 -*-
import sys
import logging
import re
import os
import esm
from bfd_brand import BrandUtils 


class BrandExtract(object):
    def __init__(self, skip_file, dot_file, char_map_file, brand_file):
        self.brand_utils = BrandUtils(dot_file=dot_file, char_map_file=char_map_file)
        self.load_brand_skip(skip_file)
        self.cn_brand_map = {}
        self.en_brand_map = {}

        self.brand_map = {}
        self.free_map = {}

        self.cn_len = 1
        self.en_len = 3

        # 纯数字品牌
        self.re_num = re.compile(u"^[0-9]+$")

        # global map
        self.cat_free = u'ALL'

        # 团购
        tuan = u"本地生活|出差旅游"
        self.re_tuan = re.compile(tuan)

        self.cid_map = {u"Cyounandu": u"有男度", u"Cosa": u"欧莎", u"Ctcl": u"tcl", u"Chuawei": u"华为"}
        logging.info('brand module init sucessfully...')

        self.init_file(brand_file)

    def load_brand_skip(self, skip_file):
        with open(skip_file, "r") as f:
            self.brand_skip = f.read().strip().decode("u8").split(u"\n")
    
    def flag_tree_cn(self, cn_name_low):
        flag_tree = (len(cn_name_low) > self.cn_len) and (not cn_name_low in self.brand_skip)
        return flag_tree
   
    def flag_tree_en(self, en_name_low):
        flag_tree = (len(en_name_low) > self.en_len) and (not self.re_num.search(en_name_low)) \
            and (not en_name_low in self.brand_skip)
        return flag_tree

    """
    def init_mysql(self, host="192.168.49.77", user="bfdroot",passwd="qianfendian",db="BfdStandardInfo",charset="utf8"):
        conn=MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset=charset)
        cursor = conn.cursor()
        cursor.execute('select id, cn_name, en_name, category, cn_alias, en_alias from standarddata_bfdbrand')
        rows = cursor.fetchall()
    
        logging.info('connect to database...')
        logging.info('load %d records...' %len(rows))

        self.init_tree(rows)
        cursor.close()
        conn.close()
        logging.info('close the database...')
    """

    def init_file(self, filename):
        with open(filename, 'r') as rfile:
            logging.info("read the brand file %s ..." %filename)
            lines = rfile.readlines()
        rows = [line.strip('\n').decode('u8').split(u'\t') for line in lines]
        self.init_tree(rows)

    def init_tree(self, rows):
        for row in rows:
            bid, cn_name, en_name, category, cn_alias, en_alias = row
            cat_str = category
            # brand_map
            cn_name_low = self.brand_utils.refine(cn_name.lower(), dot=True)
            en_name_low = self.brand_utils.refine(en_name.lower(), dot=True)

            tree = self.cn_brand_map.get(cat_str, esm.Index())
            TuanGou = self.re_tuan.match(cat_str)
            if not TuanGou:
                tree_free = self.cn_brand_map.get(self.cat_free, esm.Index())

            if cn_name_low:
                self.free_map[cn_name_low] = (bid, cn_name, en_name)
                flag_tree = self.flag_tree_cn(cn_name_low)
                if flag_tree:
                    tree.enter( cn_name_low.encode('utf-8') )
                    self.brand_map[cat_str + cn_name_low] = (bid, cn_name, en_name)
                    if not TuanGou:
                        tree_free.enter( cn_name_low.encode('utf-8') )
                        self.brand_map[self.cat_free + cn_name_low] = (bid, cn_name, en_name)
            if cn_alias:
                cn_alias_low = self.brand_utils.refine(cn_alias.lower(), dot=True)
                for keyword in cn_alias_low.split(','):
                    if keyword:
                        self.free_map[keyword] = (bid, cn_name, en_name)
                        flag_tree = self.flag_tree_cn(keyword)
                        if flag_tree:
                            tree.enter(keyword.encode('utf-8'))
                            self.brand_map[cat_str + keyword] = (bid, cn_name, en_name)
                            if not TuanGou:
                                tree_free.enter(keyword.encode('utf-8'))
                                self.brand_map[self.cat_free + keyword] = (bid, cn_name, en_name)
            self.cn_brand_map[cat_str] = tree
            if not TuanGou:
                self.cn_brand_map[self.cat_free] = tree_free

            tree = self.en_brand_map.get(cat_str, esm.Index())
            if not TuanGou:
                tree_free = self.en_brand_map.get(self.cat_free, esm.Index())

            if en_name_low:
                self.free_map[en_name_low] = (bid, cn_name, en_name)
                flag_tree = self.flag_tree_en(en_name_low)
                if flag_tree:
                    tree.enter( en_name_low.encode('utf-8') )
                    self.brand_map[cat_str + en_name_low] = (bid, cn_name, en_name)
                    if not TuanGou:
                        tree_free.enter( en_name_low.encode('utf-8') )
                        self.brand_map[self.cat_free + en_name_low] = (bid, cn_name, en_name)
            if en_alias:
                en_alias_low = self.brand_utils.refine(en_alias.lower(), dot=True)
                for keyword in en_alias_low.split(','):
                    if keyword:
                        self.free_map[keyword] = (bid, cn_name, en_name)
                        flag_tree = self.flag_tree_en(keyword)
                        if flag_tree:
                            tree.enter( keyword.encode('utf-8') )
                            self.brand_map[cat_str + keyword] = (bid, cn_name, en_name)
                            if not TuanGou:
                                tree_free.enter( keyword.encode('utf-8') )
                                self.brand_map[self.cat_free + keyword] = (bid, cn_name, en_name)
            self.en_brand_map[cat_str] = tree
            if not TuanGou:
                self.en_brand_map[self.cat_free] = tree_free

        for cat_str, tree in self.cn_brand_map.iteritems():
            try:
                tree.fix()
            except:
                self.cn_brand_map[cat_str] = None

        for cat_str, tree in self.en_brand_map.iteritems():
            try:
                tree.fix()
            except:
                self.en_brand_map[cat_str] = None 
        
    def search_long(self, result):
        ret = ""
        lr = len(ret)
        for k in result:
            lk = k[0][1] - k[0][0]
            if lk > lr:
                ret = k[1]
                lr = lk
        return ret 

    def find_match(self, tree, text):
        if tree is None:
            return None
        result = tree.query(text.encode('utf-8'))
        if result is None:
            return None
        ret = self.search_long(result)   #ret = text[result[0] : result[1]]
        return ret.decode('utf-8')

    # 文本查找
    def find_tree(self, cn_tree, en_tree, cat_str, text):
        ret = self.find_match(cn_tree, text)
        if ret:
            cn_name = ret
            try:
                bid, cn_name, en_name = self.brand_map[cat_str+cn_name]
            except:
                bid, cn_name, en_name = 0, u'', u'' 
            return (bid, cn_name if cn_name else en_name)
        ret = self.find_match(en_tree, text)
        if ret:
            en_name = ret
            try:
                bid, cn_name, en_name = self.brand_map[cat_str+en_name]
            except:
                bid, cn_name, en_name = 0, u'', u''
            return (bid, cn_name if cn_name else en_name)
        return None

    # 全局查找
    def global_map(self, brand):
        ret = self.free_map.get(brand, None)
        if ret:
            return ret
        cn_name, en_name = self.brand_utils.brand_split(brand)
        ret = self.free_map.get(cn_name, None)
        if ret:
            return ret
        ret = self.free_map.get(en_name, None)
        if ret:
            return ret
        return None

    # 特殊客户
    def cid_search(self, cid):
        brand = self.cid_map.get(cid, None)
        if brand:
            bid, cn_name, en_name = self.global_map(brand)
            return (bid, cn_name if cn_name else en_name)
 
    def find_brand(self, cat_str, name, brand, cid=None):
        # 预处理
        cid_result = self.cid_search(cid)
        if cid_result:
            return cid_result

        name = self.brand_utils.refine(name, dot=True)
        brand = self.brand_utils.refine(brand, dot=True)
        name = name.strip().lower()
        brand = brand.strip().lower()
        if brand == u'notprovided':
            brand = ''

        # 查找类目下的品牌库
        cn_tree = self.cn_brand_map.get(cat_str, None)
        en_tree = self.en_brand_map.get(cat_str, None)
        if cn_tree is None and en_tree is None:
            return None
   
        ret = None
        TuanGou = self.re_tuan.match(cat_str)
        if brand:
            try:
                if TuanGou:
                    bid, cn_name, en_name = 0, u'', u'' 
                else:
                    bid, cn_name, en_name = self.global_map(brand)
            except Exception, e:
                bid, cn_name, en_name = 0, u'', u'' 
            if bid:
                return (bid, cn_name if cn_name else en_name)
            ret = self.find_tree(cn_tree, en_tree, cat_str, brand)
            if ret:
                return ret
#            logging.error('no match brand for brand: %s, %s', cat_str.encode('utf8'), brand.encode("utf8"))

        if name and cat_str != self.cat_free:
            ret = self.find_tree(cn_tree, en_tree, cat_str, name)
            if ret:
                return ret
#        logging.error('no match brand for name: %s, %s', cat_str.encode('utf8'), name.encode("utf8"))

        # 查找所有品牌库
        if cat_str != self.cat_free and not TuanGou:
            return self.find_brand(self.cat_free, name, brand, cid)

if __name__ == '__main__':
    cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    skip_file = cur_dir + "/brand_skip.txt"
    dot_file = cur_dir + "/dot.txt"
    char_map_file = cur_dir + "/char_map.txt"
    brand_file = cur_dir + "/MAP_BRAND"
    be = BrandExtract(
                skip_file= skip_file,
                dot_file = dot_file,
                char_map_file = char_map_file,
                brand_file = brand_file)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            for line in f:
                cid, name, cat_str, brand = line.decode('utf8').strip(u'\n').split(u'\t')
                ret = be.find_brand(cat_str, name, brand)
                if ret:
                    print line.strip(),'***' ,ret[0], ret[1]
                else:
                    print line.strip(), "No Brand!"      
    else:
        ret = be.find_brand(u'运动户外', u'The North Face/北面 2013春季新款TNF女款防风防水单层冲锋衣A35D', u'北面', u'Ctcl')
        if ret:
            print ret[0], ret[1]

