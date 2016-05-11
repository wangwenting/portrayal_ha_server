# -*- coding:utf-8 -*-

import os
import jieba
try:
    import cPickle as pickle
except:
    import pickle


class GenderRule(object):
    def __init__(self, rule_path=None):
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        if not rule_path:
            rule_path = cur_dir + "/resource/rules"

        self.load_gender_rules(rule_path)
   
    def load_gender_rules(self, rule_path):
        rules_pos = []
        rules_neg = []
        rules_hed = []
        for line in open(rule_path, 'r'):
            rule_pos = []
            rule_neg = []
            l = line.strip('\n').decode("utf-8").split('    ')
            if len(l) > 1:
                rules_hed.append(l[0])
                for term in l[1:]:
                    if term.find('-') != -1:
                        rule_neg.append(term.replace('-', '').replace('{', '').replace('}', ''))
                    else:
                        rule_pos.append(term.replace('{', '').replace('}', ''))
                rules_pos.append(rule_pos)
                rules_neg.append(rule_neg)
        self.rules_pos = rules_pos
        self.rules_neg = rules_neg
        self.rules_hed = rules_hed
    
    def occur_one(self, sample, term_list):
        if len(term_list) == 0:
            return True
        for term in term_list:
            if sample.find(term)!=-1:
                return True
        return False
    
    def predict_onesample_based_rules(self, line):
        rules_hed = self.rules_hed
        rules_pos = self.rules_pos
        rules_neg = self.rules_neg
        for pos in range(len(rules_hed)):
            satisfy_rule = True
            for rule in rules_pos[pos]:
                rule = rule.strip()
                if not self.occur_one(line,rule.split(' ')):
                    satisfy_rule = False
                    break
            if not satisfy_rule:
                continue
            for rule in rules_neg[pos]:
                rule = rule.strip()
                if len(rule) and self.occur_one(line,rule.split(' ')):
                    satisfy_rule = False
                    break
            if satisfy_rule:
                if rules_hed[pos] == u'男':
                    return '1'
                elif rules_hed[pos]== u'女':
                    return '-1'
                else:
                    return '0'
        if not satisfy_rule:
            return '0'


class GenderModel(object):
    def __init__(self, model_path=None):
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        if not model_path:
            model_path = cur_dir + "/resource/l1_base_model"

        self.load_model(model_path)
   
    def load_model(self, model_path):
        fp = open(model_path, 'r')
        self.clf = pickle.load(fp)
        self.count_vect = pickle.load(fp)
        fp.close()
 
    def predict_with_threshold(self, predicted_prob,thres=1.0):
        predicted = []
        for pos in range(len(predicted_prob)):
            if predicted_prob[pos][0] > predicted_prob[pos][1]  and predicted_prob[pos][1]/predicted_prob[pos][0]<=thres:
                predicted.append('-1')
                # print '-1\t' + str(predicted_prob[pos][0])+'\t' + str(predicted_prob[pos][1])
            elif predicted_prob[pos][1] >= predicted_prob[pos][0] and predicted_prob[pos][0]/predicted_prob[pos][1]<=thres:
                predicted.append('1')
                #print '1\t'+str(predicted_prob[pos][0]) + '\t' + str(predicted_prob[pos][1])
            else:
                predicted.append('0')
                #print '0\t'+str(predicted_prob[pos][0]) + '\t' + str(predicted_prob[pos][1])
        return predicted

    def predict_base_model(self, test_data, thres):
        X_test_counts = self.count_vect.transform(test_data)
        #print 'length of test data : ' + str(len(test_data))
        predicted = self.clf.predict_proba(X_test_counts)
        predicted = predicted.tolist()
        #print predicted
        predicted = self.predict_with_threshold(predicted, thres)
        return predicted

    def format_line(self, line):
        return ' '.join(list(jieba.cut(line)))
    
    def predict_line(self, line, thres=0.25):
        return self.predict_base_model([self.format_line(line)], thres)[0]    

if __name__ == '__main__':
     gr = GenderRule()
     gm = GenderModel()
    
     sent = u"全国包邮】仅189元！尊享689元《大盛公羊》四季商务英伦女士皮鞋"
     print gr.predict_onesample_based_rules(sent)
     print gm.predict_line(sent)


