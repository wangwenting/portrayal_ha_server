# -*- coding: utf-8 -*-
import logging
import traceback

from portrayal_server.modules.module import Module

class TourType(Module):
    def __init__(self, context):
        super(TourType, self).__init__(context)

    def get_tour_type(self, cat):
        tour_type = u''
        for c in cat:
            if c.find(u'自由') != -1:
                tour_type = u'自助游'
                break
            if c.find(u'跟团') != -1:
                tour_type = u'跟团'
                break
        return tour_type

    def __call__(self, item_base, item_profile):
        try:
            cat = item_base.get("pid",[])
            item_profile["tour_type"] = self.get_tour_type(cat)
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("tour_type: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    tt = TourType(None)
    print tt.get_tour_type([u'跟团', u'自由'])
