# -*- coding: utf-8 -*-

import traceback
import json
import os
import logging

from portrayal_server.modules.module import Module
from portrayal_server.zk_config.zk_client import zk_conf
from portrayal_server.modules.new_classifier.feature_word import WordFeature
from industry import Industry
from portrayal_server.modules.new_classifier.classifier import Category, ClassifierWrap, MyPipeline


class ClassifierClient(object):
    def __init__(self, model_file=None,
                 model_yiyao_file=None,
                 punct_file=None,
                 stop_file=None,
                 once_file=None,
                 reserve_file=None,
                 area_file=None,
                 color_file=None,
                 quantifier_file=None,
                 num_file=None):

        self._classif = None
        self._classif_new = None
        self._wordfeature = WordFeature(punct_file=punct_file,
                                        stop_file=stop_file,
                                        once_file=once_file,
                                        reserve_file=reserve_file,
                                        area_file=area_file,
                                        color_file=color_file,
                                        quantifier_file=quantifier_file,
                                        num_file=num_file)
        self.init(model_file, model_yiyao_file)

    def init(self, model_file, model_yiyao_file):
        self._classif = ClassifierWrap()
        self._classif.load(model_file)

        self._classif_new = ClassifierWrap()
        self._classif_new.load(model_yiyao_file)

    @staticmethod
    def char_code(text):
        if not isinstance(text, unicode):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                text = text.decode('gbk', 'ignore')
        return text

    def classify(self, cid, name, category, brand, price):
        orig_cat = category
        cid = self.char_code(cid)
        name = self.char_code(name)
        category = self.char_code(category)
        brand = self.char_code(brand)

        config = zk_conf.get_client(cid)
        if config and "industry" in config and \
                (config["industry"] == Industry.INDUSTRY_MEDICINE or config["industry"] == Industry.INDUSTRY_ESTATE):
            cid, name, category, brand, price, sample = \
                self._wordfeature.convert_all_new(cid, name, category, brand, price)
            try:
                result, ids = self._classif_new.gridsearch_predict_ex(cid, name, category, brand, price, sample)
                return result, ids
            except Exception, e:
                traceback.print_exc()
                logging.error('classify: %s', e)
                return [], []
        else:
            cid, name, category, brand, price, sample = \
                self._wordfeature.convert_all(cid, name, category, brand, price)
            try:
                result, ids = self._classif.gridsearch_predict(cid, name, category,
                                                               brand, price, sample, orig_cat)
            except Exception, e:
                traceback.print_exc()
                logging.error('classify: %s', e)
                return [], []
            return result, ids


class ClassifierNew(Module):
    def __init__(self, context):
        super(ClassifierNew, self).__init__(context)
        logging.info("Classifier module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        model_file = cur_dir + "/out/classif.dat"
        model_yiyao_file = cur_dir + "/out/classif_yiyao.dat"
        punct_file = cur_dir + '/dict/punct.txt'
        stop_file = cur_dir + '/dict/stop_words.txt'
        once_file = cur_dir + '/dict/once.words'
        reserve_file = cur_dir + '/dict/reserve_words.txt'
        area_file = cur_dir + "/dict/city.txt"
        color_file = cur_dir + "/dict/color.txt"
        quantifier_file = cur_dir + "/dict/quantifier.txt"
        num_file = cur_dir + "/dict/num_zh.txt"
        self.classif = ClassifierClient(model_file=model_file,
                                        model_yiyao_file=model_yiyao_file,
                                        punct_file=punct_file,
                                        stop_file=stop_file,
                                        once_file=once_file,
                                        reserve_file=reserve_file,
                                        area_file=area_file,
                                        color_file=color_file,
                                        quantifier_file=quantifier_file,
                                        num_file=num_file)
        self.resource_process(model_file=model_file,
                              model_yiyao_file=model_yiyao_file,
                              punct_file=punct_file,
                              stop_file=stop_file,
                              once_file=once_file,
                              reserve_file=reserve_file,
                              area_file=area_file,
                              color_file=color_file,
                              quantifier_file=quantifier_file,
                              num_file=num_file)
        logging.info("Classifier module init end")

    def resource_process(self, model_file,
                         model_yiyao_file,
                         punct_file,
                         stop_file,
                         once_file,
                         reserve_file,
                         area_file,
                         color_file,
                         quantifier_file,
                         num_file):
        self.add_resource_file(model_file)
        self.add_resource_file(model_yiyao_file)
        self.add_resource_file(punct_file)
        self.add_resource_file(stop_file)
        self.add_resource_file(once_file)
        self.add_resource_file(reserve_file)
        self.add_resource_file(area_file)
        self.add_resource_file(color_file)
        self.add_resource_file(quantifier_file)
        self.add_resource_file(num_file)

    def __call__(self, item_base, item_profile):
        try:
            cid = item_base["cid"]
            name = item_base.get("name", None)
            pid = item_base.get("pid", None)
            brand = u" ".join(item_base.get("brand", ""))
            cat = []
            cat.extend(pid)
            cat_str = json.dumps(cat)
            price = item_base.get("price", 0)
            result_info = self.classif.classify(cid, name, cat_str, brand, price)
            item_profile["category_name_new"] = []
            item_profile["category_name_new"].extend(result_info[0])
            item_profile["category_id_new"] = []
            item_profile["category_id_new"].extend(result_info[1])
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("category_name_new: %s", e)
        return {"status": 0}


def test_classify():
    cid = u"Cmaibuxie"
    name = u"专柜正品 福联升 老北京布鞋 时尚女童鞋 单小礼仪 舞蹈鞋"
    brand = u"福联升"
    category = json.dumps([u"儿童布鞋"])
    price = 19
    cn = ClassifierNew(None)
    zk_conf.load_zk_resource(hosts="172.18.1.22:2181,172.18.1.23:2181,172.18.1.24:2181")
    result_info = cn.classif.classify(cid, name, category, brand, price)
    print json.dumps(result_info, ensure_ascii=False)

if __name__ == "__main__":
    test_classify()
