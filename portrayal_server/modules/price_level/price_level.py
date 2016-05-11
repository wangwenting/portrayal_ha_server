# coding: utf-8
import traceback
import os
import json
import logging

from portrayal_server.modules.module import Module


class PriceLevel(Module):
    def __init__(self, context):
        super(PriceLevel, self).__init__(context)
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        self.price_levels = {}
        cfg_file = cur_dir + '/resource/price_level_9.txt'
        self.load_file(cfg_file)
        self.resource_process(cfg_file)

    def resource_process(self, cfg_file):
        self.add_resource_file(cfg_file)

    def load_file(self, file):
        with open(file, 'r') as f:
            for line in f:
                cat, center, level = line.rstrip('\n').decode("u8").split('\t')
                cat_str = u'$'.join(json.loads(cat))
                if cat_str not in self.price_levels:
                    self.price_levels[cat_str] = [0] * 9
                self.price_levels[cat_str][int(level) - 1] = float(center)

    def get_price_level(self, cat_str, price):
        centers = self.price_levels.get(cat_str, None)
        if not centers:
            return None
        min_distance = 25873131
        level = 1
        i = 0
        for center in centers:
            i += 1
            distance = abs(center - price)
            if distance < min_distance:
                min_distance = distance
                level = i
        return level

    def __call__(self, item_base, item_profile):
        try:
            price = item_base.get("price", 0)
            cat_str = u"$".join(item_profile["category_name_new"])
            level = self.get_price_level(cat_str, price)
            if level:
                item_profile["price_level"] = level
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("price_level: %s", e)
        return {"status": 0}

    def probuf(self, item_base, item_profile):
        try:
            price = item_base.price
            cat_str = u"$".join( item_profile.category_name_new )
            level = self.get_price_level(cat_str, price)
            if level:
                item_profile.price_level = level
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("price_levle: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    cat_str = u'个护化妆$彩妆$底妆'
    price = 153.0
    pl = PriceLevel(None)
    print pl.get_price_level(cat_str, price)
    print pl.get_price_level(cat_str, 700)
    print pl.get_price_level(cat_str, 500)
