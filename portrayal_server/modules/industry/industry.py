# -*- coding: utf-8 -*-
import traceback
import logging

from portrayal_server.modules.module import Module
from portrayal_server.zk_config.zk_client import zk_conf


class Industry(Module):
    def __init__(self, context):
        super(Industry, self).__init__(context)

    def __call__(self, item_base, item_profile):
        try:
            cid = item_base["cid"]
            config = zk_conf.get_client(cid)
            if config and "industry" in config:
                item_profile["industry"] = config["industry"]
            else:
                item_profile["industry"] = 0
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("industry: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    ind = Industry(None)
    zk_conf.load_zk_resource(hosts='172.18.1.22:2181,172.18.1.23:2181,172.18.1.24:2181')
    print zk_conf.get_client(u'Cjinshan')['industry']
