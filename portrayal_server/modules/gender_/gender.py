# -*- coding: utf-8 -*-
import sys
import os
import logging
import traceback

from portrayal_server.modules.module import Module
from portrayal_server.modules.gender_.run import Gender


class GenderProperty(object):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class GenderRun(Module):
    def __init__(self, context):
        super(GenderRun, self).__init__(context)
        logging.info("Gender module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        path_model = cur_dir + '/resource/l1_base_model'
        rule_path = cur_dir + '/resource/rules'
        self._gender = Gender(model_path=path_model, rule_path=rule_path, threshold=0.25)
        self.resource_process(model_file=path_model, rule_file=rule_path)    
        logging.info("Gender module init end")

    def resource_process(self, model_file, rule_file):
        self.add_resource_file(model_file)
        self.add_resource_file(rule_file)    

    def gender_run(self, text):
        return self._gender.run(text)

    def __call__(self, item_base, item_profile):
        try:
            name = item_base["name"]
            cat = item_base.get("pid", [])
            line = name + " " + " ".join(cat)
            gender = self.gender_run(line)
            if gender == "-1":
                item_profile["gender"] = GenderProperty.FEMALE
            elif gender == "1":
                item_profile["gender"] = GenderProperty.MALE
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("gender: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    gender = GenderRun(None)
    print(gender.gender_run(u"全国包邮】仅189元！尊享689元《大盛公羊》四季商务英伦女士皮鞋"))
