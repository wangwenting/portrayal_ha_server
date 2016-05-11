# -*- coding: utf-8 -*-
import json
import traceback
import time

from portrayal_server.common import config_init
from portrayal_server.common import log

from portrayal_server.portrayal_pro import PortrayalPro
from portrayal_server.modules.new_classifier.classifier import Category, ClassifierWrap, MyPipeline
LOG = log.getLogger()

if __name__ == "__main__":
    try:
        config_init.parse_args(default_config_files=["/home/wenting/truck/python/portrayal_server/etc/portrayal_server/portrayal_server.conf"])
        #config_init.parse_args(default_config_files=["C:\Users\wenting\PycharmProjects\portrayal_server\etc\portrayal_server\portrayal_server.conf"])
        log.setup()
        LOG.debug("Start Test Portrayal")
        base = {}
        base["name"] = u"西安瑞祥招待所"
        base["pid"] = [u"酒店", u"西安酒店"]
        base["cid"] = "Ccaissa"
        base["iid"] = "111111"
        base["service"] = "GOOD"

        portray = PortrayalPro()
        while True:
            profile = portray.process_json(json.dumps(base), None)
            json_profile = json.loads(profile)
            print(json_profile)
            time.sleep(5)
    except Exception as e:
        LOG.error(traceback.print_exc())



