# -*- coding: utf-8 -*-
import sys
import os
import traceback
import logging

from portrayal_server.modules.module import Module
from portrayal_server.modules.bfd_brand.extract_brand import BrandExtract


class Brand(Module):
    def __init__(self, context):
        super(Brand, self).__init__(context)
        logging.info("Brand module init start")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        skip_file = cur_dir + "/resource/brand_skip.txt"
        dot_file = cur_dir + "/resource/dot.txt"
        char_map_file = cur_dir + "/resource/char_map.txt"
        brand_file = cur_dir + "/resource/MAP_BRAND"
        self.brand_extract = BrandExtract(skip_file=skip_file,
                                          dot_file=dot_file,
                                          char_map_file=char_map_file,
                                          brand_file=brand_file)
        self.resource_process(skip_file=skip_file,
                              dot_file=dot_file,
                              char_map_file=char_map_file,
                              brand_file=brand_file)
        logging.info("Brand module init end")
    def resource_process(self, skip_file, dot_file, char_map_file, brand_file):
        self.add_resource_file(skip_file)
        self.add_resource_file(dot_file)
        self.add_resource_file(char_map_file)
        self.add_resource_file(brand_file)

    def run_brand(self, cat_str, name, brand, cid):
        return self.brand_extract.find_brand(cat_str, name, brand, cid)

    def __call__(self, item_base, item_profile):
        try:
            cid = item_base["cid"]
            name = item_base["name"]
            
            brand = u" ".join(item_base.get("brand", ""))
            cat_str = ""
            if "category_name_new" in item_profile and len(item_profile["category_name_new"]):
                cat_str = item_profile["category_name_new"][0]
            brand_info = self.run_brand(cat_str, name, brand, cid)
            if brand_info:
                del item_profile["brand_name_new"][:]
                item_profile["brand_name_new"].append(brand_info[1])
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("brand_name_new: %s", e)
        return {"status": 0}

if __name__ == '__main__':
    be = Brand(None)
    ret = be.run_brand(u'运动户外', u'The North Face/北面 2013春季新款TNF女款防风防水单层冲锋衣A35D', u'北面', u'Ctcl')
    if ret:
        print ret[0], ret[1]

