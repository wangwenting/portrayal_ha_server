# -*- coding: utf-8 -*-
import traceback
import json

from thrift.transport import TSocket
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TBufferedTransport

from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.interface.portrayal.ttypes import *
from portrayal_server.protobuf.ItemProfile_pb2 import ItemProfile, ItemBase
from portrayal_server.protobuf.pbjson import pb2json


class Connection(object):
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.transport = TSocket.TSocket(ip, port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

    def connect(self):
        msg = "Connect must implement connect"
        raise  Exception(msg)

    def close(self):
        if self.transport:
            self.transport.close()


class PortrayalConnection(Connection):

    def __init__(self, ip, port, name):
        super(PortrayalConnection, self).__init__(ip, port, name)

    def connect(self):
        self.__service = PortrayalService.Client(self.protocol)
        self.transport.open()
        if not self.__service:
            raise RuntimeError("Invalid Thrift init params")

    def analyze_json(self, request, modules):
        return self.__service.analyze_json(request, modules)

    def analyze_protobuf(self, request, modules):
        return self.__service.analyze_protobuf(request, modules)

def format(values):
    for key, value in values.items():
        if not value:
            del values[key]

if __name__ == "__main__":
    con = PortrayalConnection("localhost", 10010, "Portayal")
    try:
        con.connect()
    except Exception as e:
        traceback.print_exc()
    count = 0
    while count < 1:
        count += 1
        base = {}
        base["name"] = u"女士男士专用蓝色经典欧美风格箱包皮具箱包皮具青色 天蓝色"
        base["pid"] = json.dumps( [u"箱包皮具", u"儿童箱包"] )
        base["cid"] = "Ccaissa"
        base["iid"] = "123456"
        #modules = ["item_tag_nonstd","category_name_new","brand_name_new"]
        modules = []
        for i in range(1):
            data = con.analyze_json(json.dumps(base), json.dumps(modules))
            json_file = json.loads(data)
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
        for i in range(1):
            #result = con.analyze_protobuf(item_base.SerializeToString(), json.dumps(modules))
            result = con.analyze_protobuf(item_base.SerializeToString(), json.dumps(modules))
            if result.status == 0:
                item_profile.ParseFromString(result.value)
                profile_json_ = pb2json(item_profile)
                profile_json = json.loads(profile_json_)
                format(profile_json)
                print(json.dumps(profile_json, ensure_ascii=False))
