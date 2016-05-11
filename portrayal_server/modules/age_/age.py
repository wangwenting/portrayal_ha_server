# -*- coding: utf-8 -*-
import traceback
import logging
import os

from portrayal_server.modules.module import Module
from portrayal_server.modules.age_.predict_new import AgePredict


class AgeLever(object):
    LEVEL_NULL = 0
    LEVEL_LT18 = 1
    LEVEL_18_24 = 2
    LEVEL_25_34 = 3
    LEVEL_35_49 = 4
    LEVEL_GT49 = 5


class Age(Module):
    def __init__(self, context):
        super(Age, self).__init__(context)
        logging.info("Age module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        rule_file = '%s/resource/rules.age' % cur_dir
        config_file = "%s/resource/features.cfg" % cur_dir
        self.predict = AgePredict(config_file, rule_file)
        self.resource_process(config_file, rule_file)
        logging.info("Age module init end")

    def resource_process(self, config_file, rule_file):
        self.add_resource_file(config_file)
        self.add_resource_file(rule_file)

    def __call__(self, item_base, item_profile):
        try:
            name = item_base.get("name", "")
            cat = []
            cat.extend(item_base["pid"])
            line = name + " " + " ".join(cat)
            age_cat = self.predict.predict_line(line)

            if age_cat == 0:
                item_profile["age"] = AgeLever.LEVEL_LT18
            elif age_cat == 1:
                item_profile["age"] = AgeLever.LEVEL_18_24
            elif age_cat == 2:
                item_profile["age"] = AgeLever.LEVEL_25_34
            elif age_cat == 3:
                item_profile["age"] = AgeLever.LEVEL_35_49
            elif age_cat == 4:
                item_profile["age"] = AgeLever.LEVEL_GT49
            else:
                item_profile["age"] = AgeLever.LEVEL_NULL
            logging.info("cid>iid: %s>%s age:%s", item_base["cid"], item_base["iid"], str(item_profile["age"]))
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("age: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    predict = AgePredict()
    print predict.predict_line(u"全国包邮】仅189元！尊享689元《大盛公羊》四季商务英伦皮鞋")
