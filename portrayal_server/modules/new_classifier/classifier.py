#! -*- coding: utf-8 -*-

import json
import logging
import os
import cPickle

from sklearn.pipeline import Pipeline
from item import Item
from portrayal_server.zk_config.zk_client import zk_conf


class Category:
    def __init__(self, id, names, parent_id, has_child, level, children):
        self.id = id
        self.names = names
        self.parent_id = parent_id
        self.has_child = has_child
        self.level = level
        self.children = children
        self.classifier = None
        self.gender = 0


class MyPipeline(Pipeline):
    def __init__(self, steps, category):
        super(MyPipeline, self).__init__(steps)
        self._category = category

    def predict(self, X, category=None, debug_msgs=None):
        Xt = X
        if debug_msgs is not None:
            features = category.dict_vectorizer.get_feature_names()
            out = []

            for i in range(len(Xt.indices)):
                text = u'%s %s' % (features[Xt.indices[i]], Xt.data[i])
                out.append(text)
            debug_msgs.append( u'first: ' + u', '.join(out) )
        for name, transform in self.steps[:-1]:

            Xt = transform.transform(Xt)
            if debug_msgs is not None:
                features = category.dict_vectorizer.get_feature_names()
                debug_msgs.append( u'step %s:' % transform.__class__.__name__ )
                if transform.__class__.__name__ == 'SelectPercentile':
                    Xt_new = transform.inverse_transform(Xt)
                    debug_msgs.append(output_sample(features, Xt_new.tocsr()))
                else:
                    debug_msgs.append(output_sample(features, Xt))
        return self.steps[-1][-1].predict(Xt)

    def transform_x(self, X, category=None, debug_msgs=None):
        Xt = X.copy()
        if debug_msgs is not None:
            features = category.dict_vectorizer.get_feature_names()
            out = []
            for i in range(len(Xt.indices)):
                text = u'%s %s' % (features[Xt.indices[i]], Xt.data[i])
                out.append(text)
            debug_msgs.append( u'first: ' + u', '.join(out) )
        for name, transform in self.steps[:-1]:
            Xt = transform.transform(Xt)
            if debug_msgs is not None:
                debug_msgs.append( u'step %s:' % transform.__class__.__name__ )
                if transform.__class__.__name__ == 'SelectPercentile':
                    Xt_new = transform.inverse_transform(Xt)
                    debug_msgs.append(output_sample(features, Xt_new.tocsr()))
                else:
                    debug_msgs.append(output_sample(features, Xt))
        return Xt

    def predict_ex(self, X, category=None, debug_msgs=None, cat_filter=[]):
        Xt = self.transform_x(X, category, debug_msgs)
        clf = self.steps[-1][-1]
        decision = clf.decision_function(Xt)
        if decision.ndim == 1:
            df = [0, decision.item()]
            args = [0, 1] if df[1] > 0 else [1, 0]
        else:
            df = decision.tolist()[0]
            args = decision.argsort().tolist()[0]
        args.reverse()
        if debug_msgs is not None:
            lst = []
            top = 3
            for i in args[:top]:
                line = u'%s: %s' % (category.label_encoder.classes_[i].split(u"$")[-1], df[i])
                lst.append(line)
            debug_msgs.append( u'Decision Score (Top %s):\n %s' % (top, u', '.join(lst)) )
        for i in args:
            result = category.label_encoder.classes_[i]
            if result not in cat_filter:
                return result


class ClassifierWrap(object):
    def __init__(self):
        self.root = None

    def load(self, file):
        with open(file, 'rb') as f:
            self.root = cPickle.load(f)
        return (self.root is not None)

    def find_cat(self, cat_names):
        category = self.root
        for name in cat_names:
            found = False
            for c in category.children:
                if c.names[-1] == name:
                    category = c
                    found = True
                    break
            if not found:
                return None
        return category

    def filter_stopword(self, stop_words, sample):
        for k in sample.keys():
            if k in stop_words:
                del sample[k]
        return sample

    def gridsearch_predict(self, cid, name, cat, brand, price, sample, orig_cat, max_level=3, debug_msgs=None):
        category = self.root
        cont = True

        # cat map
        dest_cat = None
        ids = []
        try:
            orig_cat_str = u'$'.join(json.loads(orig_cat))
        except Exception, e:
            logging.error("orig_cat: %s\t%s", orig_cat, e)
            orig_cat_str = ""

        config = zk_conf.get_client(cid)
        if config and "classify_map" in config and config["classify_map"]:
            for cat_map in config["classify_map"]:
                if orig_cat_str.startswith(cat_map["src_category"]):
                    dest_cat = cat_map["dst_category"].split(u"$")
                    category = self.find_cat(dest_cat)
                    ids.append(category.id)
                    if not cat_map["continue_to_classify"]:
                        if category:
                            return category.names, [category.id]
                        else:
                            return [], []
                    break
        else:
            if cat.find(u'儿童') != -1 or cat.find(u'童装') != -1:
                category = self.find_cat([u'母婴用品'])
                ids.append(category.id)

        cont = True
        sample_str = u''.join(sample.keys())
        gender = None
        if sample_str.find(u'男') != -1 and sample_str.find(u'女') == -1:
            gender = 1
        elif ((sample_str.find(u'女') != -1) or (sample_str.find(u'裙') != -1)) and sample_str.find(u'男') == -1:
            gender = 2

        if not category:
            category = self.root
        classifier = category.classifier
        result = category.names
        
        while cont:
            #print "category_name_new, ", u'$'.join(category.names).encode('u8'), len(category.children)
            #print category.gender, hasattr(category, 'gender_equivalence')
            if len(category.children) == 1:
                result = category.children[0].names
            else:
                if not hasattr(category, 'dict_vectorizer'):
                    #print u'no dict_vect:', u'$'.join(category.names)
                    #for c in category.children:
                    #    print u'$'.join(c.names)
                    if debug_msgs is not None:
                        debug_msgs.append( u'sample: %s\n' % json.dumps(sample, ensure_ascii=False) )
                    return result, ids
                
                # stop_words in special category 
                if hasattr(category, "stop_words") and category.stop_words:
                    sample = self.filter_stopword(category.stop_words, sample)
                    features = category.dict_vectorizer.transform(sample)
                else:
                    features = category.dict_vectorizer.transform(sample)
                #logging.info( 'sample: %s', json.dumps(sample, ensure_ascii=False).encode('utf-8') )

                #features = category.dict_vectorizer.transform(sample)
                predict_result = classifier.predict(features, category=category, debug_msgs=debug_msgs)
                #predict_result = classifier.predict(features)
                if debug_msgs is not None:
                    debug_msgs.append(u'')
                result = category.label_encoder.classes_[predict_result[0]]
                result = result.split(u'$')
            child_match = False
            for c in category.children:
                if c.names == result:
                    child_match = True
                    category = c
                    if gender and hasattr(c, 'gender') and gender != c.gender and hasattr(c, 'gender_equivalence'):
                        category = c.gender_equivalence
                        result = category.names
                    ids.append(category.id)
#                    classifier = category.classifier
#                    if (category.level >= 3) and (not classifier or category.has_child == 0):
                    if category.has_child == 0 or (max_level != -1 and category.level >= max_level):
                        if debug_msgs is not None:
                            debug_msgs.append( u'sample: %s\n' % json.dumps(sample, ensure_ascii=False) )
                        return result, ids
                    else:
                        classifier = category.classifier
                    break
            if not child_match:
                return result, ids

    def gridsearch_predict_ex(self, cid, name, cat, brand, price, sample, max_level=3, debug_msgs=None):
        category = self.root
        ids = []

        item = Item()
        item.load_data(cid, name, cat, brand, price, sample)
        if item.dest_cat:
            dest_cat = item.dest_cat.split(u"$")
            category = self.find_cat(dest_cat)
            if item.flag_classify_done:
                if category:
                    return category.names, [category.id,]
                else:
                    return [], []
        gender = item.gender
        cat_filter = item.cat_filter
        sample = item.sample

        if not category:
            category = self.root
        classifier = category.classifier
        
        result = category.names
        ids = []
        cont = True
        while cont:
            if len(category.children) == 1:
                result = category.children[0].names
            else:
                if not hasattr(category, 'dict_vectorizer'):
                    if debug_msgs is not None:
                        debug_msgs.append( u'sample: %s\n' % json.dumps(sample, ensure_ascii=False) )
                    return result, ids
                
                # stop_words in special category 
                if hasattr(category, "stop_words") and category.stop_words:
                    sample = self.filter_stopword(category.stop_words, sample)

                features = category.dict_vectorizer.transform(sample)
                flag_feature = features.data.any()
                if not flag_feature:
                    if debug_msgs is not None:
                        debug_msgs.append( u'feature is NULL\n' )
                        debug_msgs.append( u'sample: %s\n' % json.dumps(sample, ensure_ascii=False) )
                    return result, ids

                if category.level == 0:
                    result = classifier.predict_ex(features, category=category, debug_msgs=debug_msgs, cat_filter=cat_filter)
                else:
                    result = classifier.predict_ex(features, category=category, debug_msgs=debug_msgs, cat_filter=[])
#                    predict_result = classifier.predict(features, category=category, debug_msgs=debug_msgs)
#                    result = category.label_encoder.classes_[predict_result[0]]
                if debug_msgs is not None:
                    debug_msgs.append(u'')
                result = result.split(u'$')

            child_match = False
            for c in category.children:
                if c.names == result:
                    child_match = True
                    category = c
                    if gender and hasattr(c, 'gender') and gender != c.gender and hasattr(c, 'gender_equivalence'):
                        category = c.gender_equivalence
                        result = category.names
                    ids.append(category.id)
                    classifier = category.classifier
                    if (category.level >= 3) and (not classifier or category.has_child == 0):
                        if debug_msgs is not None:
                            debug_msgs.append( u'sample: %s\n' % json.dumps(sample, ensure_ascii=False) )
                        return result, ids
                    break
            if not child_match:
                return result, ids


if __name__ == '__main__':
    from feature_word import WordFeature
    wf = WordFeature()
    classif = ClassifierWrap()
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    classif.load(cur_dir + '/out/classif.dat')
   
    classif_new = ClassifierWrap()
    classif_new.load(cur_dir + '/out/classif_yiyao.dat')

    #cid = u"Cyiyaowang"
    cid = u""
    name = u"window/原道 T11 4GB 3G-联通 7英寸平板电脑安卓4.1通话平板电脑"
    #name = u"【青可奕】 头孢克肟胶囊 （100毫克 6粒装）"
    brand = u""
    category = json.dumps( ["0", "1"] )
    price = 0.0

    cid = u"jinshan"
    name = u"【全国包邮】仅168元，享原价693元瑞士军刀SWISSGEAR 手提斜挎15寸笔记本电脑包公文包SA5015黑色 斜挎 瑞士军刀 公文包 手提 电脑包 SWISSGEAR 黑色 笔记本 SA5015 全国"
    brand = u""
    price = 168
    category = json.dumps( [u"商品", u"箱包", u"电脑包"] )

    cid, name, category, brand, price, sample = wf.convert_all( \
         cid, name, category, brand, price)
    print "old", json.dumps(sample, ensure_ascii=False)

    result_info = classif.gridsearch_predict( \
                        cid, name, category, brand, price, sample, category)
    print json.dumps(result_info, ensure_ascii=False)

    cid, name, category, brand, price, sample = wf.convert_all_new( \
             cid, name, category, brand, price)
    print "new", json.dumps(sample, ensure_ascii=False)

    result_info = classif_new.gridsearch_predict_ex( \
             cid, name, category, brand, price, sample, category)
    print json.dumps(result_info, ensure_ascii=False)


