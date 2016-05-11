# -*- coding: utf-8 -*-
import logging
import traceback

from portrayal_server.modules.module import Module


class PstAnalyser(Module):
    def __init__(self, context):
        super(PstAnalyser, self).__init__(context)

    @staticmethod
    def set_haolemai_cats(raw_cat_str, res_cats):
        v_cat = raw_cat_str.split(u'$')
        idx = 0
        for cc in v_cat:
            if idx >= len(res_cats):
                res_cats.append(cc)
            else:
                res_cats[idx] = cc
            idx = idx + 1

    @staticmethod
    def chaolemai(cid, name):
        cat = ""
        if cid == 'Chaolemai':
            if name.find(u"包") >= 0 or name.find(u"箱") >= 0:
                if name.find(u"女士") >= 0:
                    if name.find(u"双肩") >= 0:
                        cat = u"箱包$女包$双肩包"
                    if name.find(u"书包") >= 0:
                        cat = u"箱包$女包$双肩包"
                    if name.find(u"登山包") >= 0:
                        cat = u"箱包$功能包$登山包"
                    if name.find(u"单肩") >= 0 or name.find(u"挎包") >= 0:
                        cat = u"箱包$女包$单肩包"
                    if name.find(u"手提包") >= 0:
                        cat = u"箱包$女包$手提包"
                    if name.find(u"手拎包") >= 0:
                        cat = u"箱包$女包$手提包"
                    if name.find(u"旅行包") >= 0:
                        cat = u"箱包$功能包$旅行包"
                    if name.find(u"电脑背包") >= 0:
                        cat = u"箱包$功能包$电脑数码包"
                    if name.find(u"拉杆箱") >= 0:
                        cat = u"箱包$功能包$拉杆箱"
                    if name.find(u"旅行箱") >= 0:
                        cat = u"箱包$功能包$拉杆箱"
                    if name.find(u"登机箱") >= 0:
                        cat = u"箱包$功能包$拉杆箱"
                    if name.find(u"卡包") >= 0:
                        cat = u"箱包$女包$钱包/卡包"
                    if name.find(u"名片包") >= 0:
                        cat = u"箱包$女包$钱包/卡包"
                    if name.find(u"钱包") >= 0:
                        cat = u"箱包$女包$钱包/卡包"
                    if name.find(u"腰包") >= 0:
                        cat = u"箱包$功能包$胸包/腰包"
                    if name.find(u"便携背包") >= 0:
                        cat = u"箱包$功能包$旅行包"
                    if name.find(u"皮肤包") >= 0:
                        cat = u"箱包$功能包$运动休闲包"

                else:
                    if name.find(u"双肩") >= 0:
                        cat = u"箱包$男包$双肩包"
                    if name.find(u"书包") >= 0:
                        cat = u"箱包$男包$双肩包"
                    if name.find(u"登山包") >= 0:
                        cat = u"箱包$功能包$登山包"
                    if name.find(u"单肩") >= 0 or name.find(u"挎包") >= 0:
                        cat = u"箱包$男包$单肩包"
                    if name.find(u"手提包") >= 0:
                        cat = u"箱包$男包$手提包"
                    if name.find(u"手拎包") >= 0:
                        cat = u"箱包$男包$手提包"
                    if name.find(u"旅行包") >= 0:
                        cat = u"箱包$功能包$旅行包"
                    if name.find(u"电脑背包") >= 0:
                        cat = u"箱包$功能包$电脑数码包"
                    if name.find(u"拉杆箱") >= 0:
                        cat = u"箱包$功能包$拉杆箱"
                    if name.find(u"旅行箱") >= 0:
                        cat = u"箱包$功能包$拉杆箱"
                    if name.find(u"登机箱") >= 0:
                        cat = u"箱包$功能包$拉杆箱"
                    if name.find(u"卡包") >= 0:
                        cat = u"箱包$男包$钱包/卡包"
                    if name.find(u"名片包") >= 0:
                        cat = u"箱包$男包$钱包/卡包"
                    if name.find(u"钱包") >= 0:
                        cat = u"箱包$男包$钱包/卡包"
                    if name.find(u"腰包") >= 0:
                        cat = u"箱包$功能包$胸包/腰包"
                    if name.find(u"便携背包") >= 0:
                        cat = u"箱包$功能包$旅行包"
                    if name.find(u"皮肤包") >= 0:
                        cat = u"箱包$功能包$运动休闲包"
        return cat

    def __call__(self, item_base, item_profile):
        try:
            cid = item_base["cid"]
            name = item_base["name"]
            cat = self.chaolemai(cid, name)
            if cat:
                self.set_haolemai_cats(cat, item_profile["category_name_new"])
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("PreAnalyser: %s", e)
        return {"status": 0}
