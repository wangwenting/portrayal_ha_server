# -*- coding: utf-8 -*-

import jieba
from gender_predict import GenderRule, GenderModel


class Gender: 
    def __init__(self, model_path, rule_path, threshold=0.25):
        self.rule = GenderRule(rule_path)
        self.model = GenderModel(model_path)
        self.threshold = threshold

    def format_line(self, line):
        return ' '.join(list(jieba.cut(line)))

    def predict_line(self, line):
        _predict = self.rule.predict_onesample_based_rules(line)
        if _predict != '0':
            return _predict
        return self.model.predict_base_model([self.format_line(line)], self.threshold)[0]
    
    def run(self, line):
        if not isinstance(line, unicode):
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError:
                line = line.decode('gbk', 'ignore')
        return self.predict_line(line)

if __name__ == '__main__':
    import os
    cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    path_model = cur_dir + '/resource/l1_base_model'
    rule_path = cur_dir + '/resource/rules'
    gender = Gender(model_path=path_model, rule_path=rule_path)
    print gender.run('童装女童夏装2013新款儿童吊带连衣裙韩版纯棉无袖背心裙牛仔裙子')
