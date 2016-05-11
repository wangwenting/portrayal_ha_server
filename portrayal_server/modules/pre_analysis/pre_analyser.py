# -*- coding: utf-8 -*-
import logging
import traceback

from portrayal_server.modules.module import Module


class PreAnalyser(Module):
    def __init__(self, context):
        super(PreAnalyser, self).__init__(context)

    def __call__(self, item_base, item_profile):
        try:
            if item_base["cid"] == "Chaolemai":
                item_base["name"] = "%s %s" %(item_base["name"], item_base["subtitle"])
                logging.debug("In pre-Analyser, It's haolemai, need special process, new name: %s" %item_base["name"])
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("PreAnalyser: %s", e)
        return {"status": 0}