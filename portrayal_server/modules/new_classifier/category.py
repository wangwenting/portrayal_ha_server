#! -*- coding:utf-8 -*-

import sys, os, json, cPickle, logging


class Category(object):
    def __init__(self, cid, names, parent_id, has_child, level, children):
        self.cid = cid
        self.names = names
        self.parent_id = parent_id
        self.has_child = has_child
        self.level = level
        self.children = children
        self.classifier = None
        self.gender = 0
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
   
    def _cate_gender(self):
        if self.level > 1:
            has_gender = False
            names = self.names
            if (names[-1].find(u'男') != -1) and (names[-1].find(u'女') == -1):
                self.gender = 1
                has_gender = True
            elif (names[-1].find(u'女') != -1) and (names[-1].find(u'男') == -1):
                self.gender = 2
                has_gender = True
 
    def _load_stop_words(self):
        name_str = u'$'.join(self.names)
        name_str = name_str.replace(u'/', u'_') 
        words_dir = '%s/dict/stop_words/%s.txt' %(self.cur_dir, name_str)
        stop_words = set()
        if os.path.isfile(words_dir):
            with open(words_dir, 'r') as f:
                for line in f:
                    stop_words.add(line.strip('\n').decode('utf-8'))
                logging.info('%s has %d stop_words', name_str, len(stop_words))
        self.stop_words = stop_words

    @staticmethod
    def _read_param():
        params = {}
        with open('out/params.txt', 'r') as f:
            for line in f:
                cat_name, params_str, score = line.rstrip('\n').split('\t')
                current_params = {}
                for k, v in json.loads(params_str).iteritems():
                    if '.' in v or 'e' in v:
                        current_params[k] = float(v)
                    else:
                        current_params[k] = int(v)
                params[cat_name] = current_params
        return params

    def _get_cate_param(self, params):
        if not params:
            params = Category._read_param()
        self.best_parameters = params.get(json.dumps(self.names, ensure_ascii=False).encode('utf-8') , {})
           
    def read_cat_from_db(self):
        pass
 
    @staticmethod
    def read_cat_from_file(catfile):
        top_cats = []
        cats = []
        params = Category._read_param()
        with open(catfile, 'r') as f:
            for line in f:
                cid, name, parent_id, has_child, level = line.strip('\n').split('\t')
                if int(level) > 3:
                    continue

                if not has_child:
                    has_child = 0
                names = json.loads(name)
                level = len(names)
                cat = Category(cid, names, parent_id, has_child, level, [])
                cat._cate_gender()
                cat._load_stop_words()
                cat._get_cate_param(params)
                cats.append(cat)

                if cat.level == 1:
                    top_cats.append(cat)
          
            for cat in cats:
                if cat.level != 1:
                    found = filter(lambda c: c.cid == cat.parent_id, cats)
                    if found:
                        parent = found[0]
                        parent.children.append(cat)
                        #print 'add child %s to %s' %(json.dumps(cat.names, ensure_ascii=False).encode('utf-8'), json.dumps(parent.names, ensure_ascii=False).encode('utf-8'))
                    else:
                        logging.error('not found category: %s', parent_id)      
            
        root = Category(0, [], 0, 1, 0, top_cats)
        root._get_cate_param(params)
        return root

    @staticmethod
    def read_cat_from_db():
        pass

    def dump(self, dumpfile):
        with open(dumpfile, 'wb') as f:
            cPickle.dump(self, f)  

    @staticmethod
    def load(dumpfile):
        with open(dumpfile, 'rb') as f:
             return cPickle.load(f)
        return None

    @staticmethod
    def pretty_print(category):
        for cate in category.children:
            name = cate.names[cate.level-1].encode('utf-8')
            if cate.level == 1:
                print name
            else: 
                print " |------"*(cate.level-1), name
            Category.pretty_print(cate)


if __name__ == '__main__':
    cat = Category('123', 'aaa', 0, 1, 0, ['1','2','3'])
    #cat.dump('abc')
    #cat2 = cat.load('abc')
    #print cat2.names, cat2.children
    #cat3 = Category.read_cat_from_file('abc')
    #print cat3.names, cat3.children
    cat4 = Category.read_cat_from_file('CATE_MAP_ALL')
    Category.pretty_print(cat4)
