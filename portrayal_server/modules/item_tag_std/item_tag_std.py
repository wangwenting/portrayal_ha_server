# -*- coding: utf-8 -*-
import traceback
import logging
import os

from portrayal_server.modules.module import Module
from portrayal_server.modules.item_tag_std.es_client import ESClient

class ItemTagStd(Module):
    def __init__(self, context):
        super(ItemTagStd, self).__init__(context)
        logging.info("item tag standard module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        config_file = "%s/elasticsearch.cfg" % cur_dir
        self.es_client = ESClient(config_file)
        self.resource_process(config_file)
        logging.info("item tag standard module init end")

    def resource_process(self, config_file):
        self.add_resource_file(config_file)

    def __call__(self, item_base, item_profile):
        try:
            name = item_base.get("name", "")
            category = item_profile.get("category_name_new", "")

            result = self.es_client.commodity2product(name)
            item_profile["attr"] = json.dumps( result.get("attr_str",{}), ensure_ascii= False)
            item_profile["product_name"] = result.get("name", "")

            logging.info("cid>iid: %s>%s product_name:%s", item_base["cid"], item_base["iid"], str(item_profile["product_name"]))
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("attr: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    its = ItemTagStd(None)
    print its.es_client.commodity2product(u"")
