# -*- coding: utf-8 -*-
import sys
import numpy as np
import jieba
import os
import logging

logging.getLogger().setLevel(logging.DEBUG)


class AgeMapping(object):
    def __init__(self, config_file=None):
        self.AGE = ['<18', '18-24', '25-34', '35-49', '>49']
        #age classes
        self.c_age = range(5)

        #age distribution
        #d_age = [0.158, 0.377, 0.258, 0.137, 0.07]
        #d_age = [0.098, 0.271, 0.351, 0.217, 0.063]
        self.d_age = [1] * len(self.AGE)
        #tags in age
        self.t_age = [[],[],[],[],[]]
        self.feature_dict = {}

        self.load_resource(config_file)

    def load_resource(self, config_file):
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        if not config_file:
            config_file = '%s/resource/features.cfg' % cur_dir

        self.init_t_age(config_file)
        self.map_feature_dict()
        logging.info("age module map init sucessfully")
   
    def init_t_age(self, config_file):
        for line in open(config_file):
            chunks = line.strip('\n').decode("utf-8").split(':')
            tag = int(chunks[0])
            for item in chunks[1].split():
                word,weight = item.split('/')
                self.t_age[tag].append([word, float(weight)])
    
        _sum = [0.0] * len(self.t_age)
        for i in range(len(self.t_age)):
            for word in self.t_age[i]:
                _sum[i] += float(word[1])
        #wei.huang change 
        __sum = np.sum(_sum)
        for i in range(len(self.t_age)):
            for word in self.t_age[i]:
                word[1] = float(word[1]) / __sum #float(_sum[i])

    def map_feature_dict(self):
        _t_age = self.t_age
        for i in range(len(_t_age)):
            for item in _t_age[i]:
                feature, weight = item[0], float(item[1])
                if not self.feature_dict.has_key(feature):
                    self.feature_dict[feature] = [0.0] * len(_t_age)
                self.feature_dict[feature][i] = weight

    def get_word_proba(self, word):
        if not self.feature_dict.has_key(word):
            return np.asarray([0] * len(self.c_age))
        probo = []
        for i in self.c_age:
            if not self.feature_dict.has_key(word):
                probo.append(0)
            else:
                probo.append(self.feature_dict[word][i] * self.d_age[i])
        return np.asarray(probo)

    @staticmethod
    def normalization(num_list):
        _sum = sum(num_list)
        return [float(i) / _sum for i in num_list]

    def get_proba(self, string):
        words = list(jieba.cut(string))
        proba = np.asarray([0.0] * len(self.c_age))
        for word in words:
            p = self.get_word_proba(word)
            #print word,p
            proba += p
        if np.sum(proba) == float(0):
            return None
        return self.normalization(proba)

    def mapping(self, string):
        proba = self.get_proba(string)
        if proba != None:
            return str(list(proba).index(np.max(proba)))
        return None


if __name__ == '__main__':
    am = AgeMapping()
    proba = am.get_proba(u"中老年的衣服稳重成熟")
    print proba
    if proba != None:
        print am.AGE[list(proba).index(np.max(proba))]
    else:
        print None
