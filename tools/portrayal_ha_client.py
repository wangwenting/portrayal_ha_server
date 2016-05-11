# -*- coding: utf-8 -*-
import traceback
import json

from thrift.transport import TSocket

from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.interface.portrayal.ttypes import *
from portrayal_server.protobuf.ItemProfile_pb2 import ItemProfile, ItemBase
from portrayal_server.protobuf.pbjson import pb2json
from bfd.harpc import client
from bfd.harpc.common import config


def format(values):
    for key, value in values.items():
        if not value:
            del values[key]


if __name__ == "__main__":
    conf = config.Config("./etc/demo_client.conf")
    manager = client.Client(PortrayalService.Client, conf)
    proxy_client = manager.create_proxy()
    count = 0
    while count < 1:
        count += 1
        base = {}
        base["name"] = u"女士男士专用蓝色经典欧美风格箱包皮具箱包皮具青色 天蓝色"
        base["pid"] = json.dumps( [u"箱包皮具", u"儿童箱包"] )
        base["cid"] = "Ccaissa"
        base["iid"] = "123456"
        modules = []
        for i in range(1):
            file = proxy_client.analyze_json(json.dumps(base), json.dumps(modules))
            print file
            json_file = json.loads(file)
            json_value = json_file["value"]
            format(json_value)
            print(json.dumps(json_value, ensure_ascii=False))
        print "-------------------------"
        item_base = ItemBase()
        item_profile = ItemProfile()
        item_base.name = u"女士男士专用蓝色经典欧美风格箱包皮具箱包皮具青色 天蓝色"
        item_base.pid.extend([u"箱包皮具", u"儿童箱包"])
        item_base.cid = "Ccaissa"
        item_base.iid = "123456"
        for i in range(1000):
            #result = con.analyze_protobuf(item_base.SerializeToString(), json.dumps(modules))
            result = proxy_client.analyze_protobuf(item_base.SerializeToString(), json.dumps(modules))
            if result.status == 0:
                item_profile.ParseFromString(result.value)
                profile_json_ = pb2json(item_profile)
                profile_json = json.loads(profile_json_)
                format(profile_json)
                print(json.dumps(profile_json, ensure_ascii=False))
        
    manager.close()
