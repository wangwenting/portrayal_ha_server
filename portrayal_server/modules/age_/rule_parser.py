# -*- coding: utf-8 -*-
import os
import re
import logging


class RuleParser(object):
    def __init__(self, rule_path=None):
        self.load_resource(rule_path)

    def load_resource(self, rule_path):
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        if not rule_path:
            rule_path = '%s/resource/rules.age' % cur_dir
        self.init_parser(rule_path)   

    def init_parser(self, rule_path):
        '''
            init the parser by reading the rule file
        '''
        rules = []
        try:
            for line in open(rule_path):
                line = line.strip('\n').decode("utf-8")
                tag = int(line[ : line.find(':')])
                if line.find('+{') < 0:
                    positive = []
                else:
                    positive = re.match('.*\+\{(.*?)\}', line).groups()[0].split()
                if line.find('-{') < 0:
                    negative = []
                else:
                    negative = re.match('.*\-\{(.*?)\}', line).groups()[0].split()

                if line.find('U') < 0:
                    rules.append((tag, positive, negative, None, []))
                else:
                    line = line[line.find('U') : ]
                    if line.find('+{') >= 0:
                        flag = 1
                        _add = re.match('.*\+\{(.*?)\}', line).groups()[0].split()
                    if line.find('-{') >= 0:
                        flag = -1
                        _add = re.match('.*\-\{(.*?)\}', line).groups()[0].split()
                    rules.append((tag, positive, negative, flag, _add))
        except Exception, e:
            logging.error('age module rule parser init error %s' % e)
       
        logging.info("age module rule init complete")
        self.rules = rules 
    
    @staticmethod
    def inside(words, sentence):
        for word in words:
            if sentence.find(word) > 0:
                return True
        return False


    def judge(self, x):
        for rule in self.rules:
            if len(rule[1]) > 0:
                if not self.inside(rule[1], x):  continue
            if len(rule[2]) > 0:
                if self.inside(rule[2], x):  continue
        
            if rule[3] == 1:
                if not self.inside(rule[4], x):  continue
            if rule[3] == -1:
                if self.inside(rule[4], x):  continue
        
            return rule[0]
        return None


if __name__ == '__main__':
    rp = RuleParser()
    print rp.judge(u'中老年')
