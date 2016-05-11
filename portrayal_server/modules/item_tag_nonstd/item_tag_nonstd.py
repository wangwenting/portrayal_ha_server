# -*- coding: utf-8 -*-
import traceback
import logging
import os
import ConfigParser
import json

from portrayal_server.modules.module import Module
from portrayal_server.modules.item_tag_nonstd.Itemmatch import Itemmatch 
from matchHandle import matchhandle

class ItemTagNonStd(Module):
    def __init__(self, context):
        super(ItemTagNonStd, self).__init__(context)
        logging.info("item tag standard module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        config_file = "%s/resource/file.cfg" % cur_dir
        self.esm_client = Itemmatch()
        self.init_esm(config_file, cur_dir+"/resource")
        self.resource_process(config_file)
        logging.info("item tag standard module init end")

    def init_esm(self, cfg_name, dir):
        parse = ConfigParser.ConfigParser()
        parse.read(cfg_name)
        items = parse.items("category_map")

        for key, file in items:
            path = os.path.join(dir, file)
            self.esm_client.init_category_esm(key, path)
            self.add_resource_file(path)

    def resource_process(self, config_file):
        self.add_resource_file(config_file)

    def merger_result(self, result, color_result):
        if result!={} and color_result!={}:
            for key in color_result:
                if result.has_key(key):
                    result[key] = list(set(result[key]+color_result[key]))
                else:
                    result[key] = color_result[key]
        elif result=={} and color_result!={}:
            result = color_result
        return result

    def __call__(self, item_base, item_profile):
        try:
            name = item_base.get("name", "")
            attr = item_base.get("attr", "")
            title = name + attr
            category = item_profile.get("category_name_new", "")
            #打颜色标签
            color_result = {}
            try:
                color_result = self.esm_client.texttotag(name, "颜色".decode('utf-8'))
                color_result = json.loads(color_result) if color_result!="" else {}
            except Exception as e:
                logging.error("error: %s", e)

            result = {}
            cat = " "
            try:
                if category != "":
                    cat = category[0]
                    result = self.esm_client.texttotag(title, cat)
                    result = json.loads(result) if result!="" else {}
            except Exception as e:
                logging.error("error : %s", e)
            result = self.merger_result(result, color_result)
            if result!={}:
                #规则匹配
                result = matchhandle(result, title, cat)
                item_profile["attr"] = json.dumps(result, ensure_ascii=False)
                #logging.info("cfs>%s, attr>%s" %(name, item_profile['attr']))

        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("attr: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    itns = ItemTagNonStd(None)
    print itns.esm_client.texttotag(u"纯棉宝石蓝斜跨包男女通用", u"文本平台")
