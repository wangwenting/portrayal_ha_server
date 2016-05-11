# -*- coding: utf-8 -*-
import sys, logging

import jieba
import numpy as np

from rule_parser import RuleParser
from mapping_new import AgeMapping


class AgePredict(object):
    def __init__(self, config_file=None, rule_file=None):
        self.rule = RuleParser(rule_file)
        self.mapping = AgeMapping(config_file)

    def predict_cut(self, string):
        return list(set(jieba.cut(string.strip())))

    def predict_line_base_model(self, line, print_proba=False, threshold=0):
        X = self.predict_cut(line)
        proba = self.mapping.get_proba(' '.join(X))
        if proba == None or np.max(proba) <= threshold:
            return None
        if print_proba:
            print [round(i,2) for i in proba]
        return list(proba).index(np.max(proba))


    def predict_line_base_rule(self, line):
        return self.rule.judge(line)

    def predict_line(self, line, print_proba=False, threshold=0):
        if not isinstance(line, unicode):
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError:
                line = line.decode('gbk', 'ignore')
        c = self.predict_line_base_rule(line)
        if c == None:
            c = self.predict_line_base_model(line, print_proba, threshold)
        return c

if __name__ =='__main__':
    ap = AgePredict() 
    print ap.predict_line(u"全国包邮】仅189元！尊享689元《大盛公羊》四季商务英伦皮鞋", print_proba=True)
