#! -*- coding:utf-8 -*-

import os
import logging
import re
import json
import math
import traceback
from segment import Segmenter
from dict.word_label import WordLabel

from portrayal_server.zk_config.zk_client import zk_conf


class WordFeature(object):
    def __init__(self, punct_file=None,
                 stop_file=None,
                 once_file=None,
                 reserve_file=None,
                 area_file=None,
                 color_file=None,
                 quantifier_file=None,
                 num_file=None):

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if not punct_file:
            punct_file = cur_dir + '/dict/punct.txt'
        if not stop_file:
            stop_file = cur_dir + '/dict/stop_words.txt'
        if not once_file:
            once_file = cur_dir + '/dict/once.words'
        if not reserve_file:
            reserve_file = cur_dir + '/dict/reserve_words.txt'
     
        self.segmenter = Segmenter()
        self.punct = set()
        self.load_punct = (punct_file)
 
        self.stop_words = set()
        self.load_stop_words(stop_file)
 
        self.remove_words = set()
        self.load_remove_words(once_file)
 
        self.reserve_words = set()
        self.load_reserve_words(reserve_file)

        self.replace_lst = [(u'斜跨包', u'斜挎包'), (u'！', u','), (u'。', u','), (u'，', u','),
                (u'市场价', u''), (u'全国包邮', u''), (u'包邮', u''), (u'【', u''),
                (u'】', u''), (u'[', u''), (u']', u''), (u'《', u''), (u'》', u'')]

        self.word_label = WordLabel(area_file=area_file,
                                    color_file=None, quantifier_file=None, num_file=None)

    def _add_char_to_set(self, myset, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            for l in lines:
                lines = l.rstrip('\n').decode('utf-8')
                for c in lines:
                    myset.add(c)
    
    def load_punct(self, filename):
        self._add_char_to_set(self.punct, filename)

    def load_stop_words(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                self.stop_words.add(line.rstrip('\n').decode('utf-8'))

    def load_remove_words(self, filename): 
        with open(filename, 'r') as f:
             for line in f:
                 self.remove_words.add(line.rstrip('\n').decode('utf-8'))

    def load_reserve_words(self, filename):
        with open(filename, 'r') as f:
             for line in f:
                 self.reserve_words.add(line.rstrip('\n').decode('utf-8').lower()) 

    def check_is_mode(self, word):
        has_hyphen = False
        for c in word:
            if c == u'-':
                has_hyphen = True
            if (c < u'a' and c > u'z') and (c < u'0' and c > u'9'):
                return False
        return has_hyphen
    
    def check_valid_new(self, word):
        if word in self.reserve_words:
            return True
        if not word:
            return False
        if word.isnumeric():
            return False
        # unicode 编码无法使用 isalnum()
        if word.encode("u8").isalnum() and len(word) <= 3:
            return False
    #    if len(word) == 1 and ord(word) < 256:
        if len(word) == 1:
            return False
        if word in self.punct:
            return False
        if word in self.stop_words:
            return False
        if word in self.remove_words:
            return False
        if self.check_is_mode(word):
            return False
        try:
            float(word)
            return False
        except:
            pass
        return True
    

    def check_valid(self, word):
        if not word:
            return False
        if word.isnumeric():
            return False
        if word in self.punct:
            return False
        if len(word) == 1 and ord(word) < 256:
            return False
        if word[0].isdigit():
            return False
        if word in self.stop_words:
            return False
        if word in self.remove_words:
            return False
        if self.check_is_mode(word):
            return False
        return True  

    def convert_word_features(self, text):
        words = self.segmenter.segment(text.lower().strip())
        features = {}

        word0 = ""
        for word in words:
            word = word.strip().replace(u'（', u'').replace(u'）', u'').replace(u'(', u'').replace(u')', u'')
            if not word:
                continue
            word = self.word_label.word_label(word, word0)
            word0 = word
            if not self.check_valid(word):
                continue
            features[word] = 1
        return features

    def convert_all(self, cid, name, cat, brand, price):
        remove_cat_count = 0
        try:
            config = zk_conf.get_client(cid)
            if config and "category_remove" in config:
                remove_cat_count = config["category_remove"]
        except Exception, e:
            logging.error("category_remove: %s", e)

        try:
            cat= json.dumps(json.loads(cat)[remove_cat_count:], separators=(',',':'), ensure_ascii=False)
        except:
            cat = u'[]'
        if brand.endswith(u'公司'):
            brand = u''
        name = self.extract_sentence(name)
        sample = self.convert_features_with_all(name, cat, brand, price)
        return (cid, name, cat, brand, price, sample)
    
    def convert_all_new(self, cid, name, cat, brand, price):
        #    remove_cat_count = settings.REMOVE_CAT_COUNT.get(cid, 0)
        remove_cat_count = 0
        try:
            config = zk_conf.get_client(cid)
            if config and "category_remove" in config:
                remove_cat_count = config["category_remove"]
        except Exception, e:
            logging.error("category_remove: %s", e)

        try:
            cat= json.dumps(json.loads(cat)[remove_cat_count:], separators=(',',':'), ensure_ascii=False)
        except:
            cat = u'[]'
        if brand.endswith(u'公司'):
            brand = u''
        features = {}
        name = self.extract_sentence(name)
        sample = self.convert_features_with_all(name, cat, brand, price, is_new=True)
        features.update(sample)
        return (cid, name, cat, brand, price, features)

    def convert_features_with_all(self, name, category, brand, price, is_new=False):
        try:
            cat = json.loads(category)
            to_delete = []
            if brand.find(u'["') != -1:
                brand = brand.replace(u'[',u'').replace(u']',u'').replace(u'"',u'')
            if cat:
                for i in range(len(cat) - 1):
                    if cat[i].find(brand) != -1:
                        cat[i] = cat[i].replace(brand, u'')
                    if cat[i].find(u'/') != -1:
                        segs = cat[i].split(u'/')
                        if len(segs) == 2 and abs(len(segs[0]) - len(segs[1])) <= 1:
                            to_delete.append(cat[i])
                    else:
                        for j in range(i+1, len(cat)):
                            if cat[i].find(cat[j]) != -1:
                                to_delete.append(cat[i])
                for c in to_delete:
                    if c in cat:
                        cat.remove(c)
                category_new = u' '.join(cat)
            else:
                category_new = u''
        except Exception,e:
            logging.error('except: %s, %s', e, category)
            traceback.print_exc()
            category_new = category
        text = name + u' ' + category_new + u' ' + brand
        text = text.replace(u'《', u'').replace(u'》', u'').lower().strip().encode('utf-8')
        
        if is_new:
            features = self.convert_features(text)
        else:
            words = self.segmenter.segment(text)
            features = {}
            for word in words:
                try:
                    word = word.decode('utf-8').strip().replace(u'（', u'').replace(u'）', u'').replace(u'(', u'').replace(u')', u'')
                except:
                    word = u''
                if not self.check_valid(word):
                    continue
                #features[word] = features.get(word, 0) + 1
                features[word] = 1

        if brand == u'None':
            brand = u''
        #if brand:
        #    features_brand = convert_features(brand)
        #    for feature, c in features_brand.iteritems():
        #        features[u'brand_' + feature] = 1
        if is_new:
            self.add_price_feature(features, price, 10000)
        else:
            self.add_price_feature(features, price, 1)
        #print 'features: ', json.dumps(features, ensure_ascii=False).encode('utf-8')
        return features    

    def convert_features(self, text):
        words = self.segmenter.segment(text.lower().strip())
        features = {}
        word0 = ""
        #    logging.info( json.dumps(words, ensure_ascii=False) )
        for word in words:
            word = word.strip().decode('utf-8').replace(u'（', u'').replace(u'）', u'').replace(u'(', u'').replace(u')', u'')
            if not word:
                continue
            word = self.word_label.word_label(word, word0)
            word0 = word
            if not self.check_valid_new(word):
                continue
            features[word] = 1
        return features   

    def feat_category(self, category):
        if category and category != u'':
            cat = json.loads(category)
            category_new = u' '.join(cat)
        else:
            category_new = u''
        return category_new

    def feat_brand(self, brand):
        if not brand or brand == u'None' or brand == u'Null' or brand.endswith(u'公司'):
            return u''
        elif brand.find(u'["') != -1:
            brand = brand.replace(u'[',u'').replace(u']',u'').replace(u'"',u'')        
        return brand
    
    def add_price_feature(self, features, price, thre=10000):
        if type(price) is str:
            try:
                price = float(price)
            except:
                price = 0

        if price > thre:
            feature_price = u'price_%d' % int(round(math.log10(price)))
            features[feature_price] = 1        

    def extract_sentence(self, text):            
        text = text.replace(u'斜跨包', u'斜挎包').replace(u'!', u',').replace(u'！', u',').replace(u'。', u',').replace(u'，', u',').replace(u'市场价', u'').replace(u'全国包邮', u'').replace(u'包邮', u'').replace(u'【', u'').replace(u'】', u'').replace(u'[', u'').replace(u']', u'')
        text = re.sub(u'仅[0-9.]*元', u'', text)
        text = re.sub(u'仅售[0-9.]*元', u'', text).replace(u'仅售', u'')
        sentences = text.split(u',')
        if len(sentences) < 4:
            return text
        results = []
        for sentence in sentences:
            results.append(sentence)
            if len(sentence.encode('utf-8')) > 45: 
                break
        if (text.find(u'女') != -1 or text.find(u'裙') != -1 or text.find(u'美腿') != -1 ) and text.find(u'男') == -1:         
            results.append(u'女')    
        elif text.find(u'男') != -1 and (text.find(u'女') == 1 and text.find(u'裙') == -1 and text.find(u'美腿') == -1 ):        
            results.append(u'男')    
        return u' '.join(results)


    def transform_area(self, word_feats):
        to_delete = []
        area_cnt = 0
        out_cnt = 0
        for word, value in word_feats.iteritems():
            if word.startswith('color__'):
                to_delete.append(word)
            elif word.startswith('area__'):
                to_delete.append(word)
                area_cnt += 1
            elif word.startswith('out__'):
                to_delete.append(word)
                out_cnt += 1

        for key in to_delete:
            del word_feats[key]       

        if area_cnt != 0:
            word_feats["area__%d" % area_cnt] = 1 
        if out_cnt != 0:
            word_feats["out__%d" % out_cnt] = 1
        return word_feats

if __name__ == '__main__':
    wf = WordFeature()
    features = wf.convert_all('', u'杭州红色专卖53°茅台镇酱香世家10年陈酿500ml，全国包邮', u'["美食特产","酒类","白酒"]', u'五粮液', 1000)
    # features = wf.transform_area(features)
    features2 = wf.convert_all_new('', u'杭州红色专卖53°茅台镇酱香世家10年陈酿500ml    全国包邮', u'["美食特产","酒类","白酒"]', u'五粮液', 1000)
    print json.dumps(features, ensure_ascii=False).encode('utf-8')
    print json.dumps(features2, ensure_ascii=False).encode('utf-8')

