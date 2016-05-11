# -*- coding: utf-8 -*-
import traceback
import logging
import os

from portrayal_server.modules.module import Module
from portrayal_server.modules.district.extract_district import DistrictExtract
# 城市 经纬度放在 mysql 里，查询数据 获取成功后序列化成 probuf 并存入  redis


class DistrictCity(Module):
    def __init__(self, context):
        super(DistrictCity, self).__init__(context)
        logging.info("district city module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        map_file = cur_dir + "/resource/MAP_DISTRICT"
        cfg_file = cur_dir + "/resource/district.conf"
        self.district = DistrictExtract(mapfile=map_file, cfgfile=cfg_file)
        logging.info("district city module init end")
        self.resource_process(map_file=map_file, conf_file=cfg_file)

    def resource_process(self, map_file, conf_file):
        self.add_resource_file(map_file)
        self.add_resource_file(conf_file)

    def run_district(self, cid_, coord_lst_, address_, location_):
        districts_, cities_ = self.district.extract_district(cid_, coord_lst_, address_, location_)
        return districts_, cities_
        
    def __call__(self, item_base, item_profile):
        try:
            cid = item_base["cid"]
            coord_lst = []
            coord = item_base.get("coord", [])
            for x in coord:
                coord_lst.append([x["latitude"], x["longitude"]])
            addr = item_base.get("address", "")
            location = item_base.get("location", [])
            districts, cities = self.district.extract_district(cid, coord_lst, addr, location)
            if coord_lst or addr:
                del item_profile["districts"][:]
                item_profile["city"] = u""
                if len(districts) > 0:
                    if cities.count(cities[0]) == len(cities):
                        item_profile["city"] = cities[0]
                    item_profile["districts"].extend(districts)
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("districts_city: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    plugin = DistrictCity(None)
    cid = u"Cjinshan"
    location = [u"三亚"]
    addr = u"明珠广场对面"
    coord_lst = []
    districts, cities = plugin.run_district(cid, coord_lst, addr, location)
    print u" ".join(districts)
    print u" ".join(cities)
