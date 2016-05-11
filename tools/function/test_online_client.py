import os
import traceback
import logging
import json
#import redis
import multiprocessing
import time
import PyBfdRedis


from portrayal_server.protobuf.pbjson import pb2json, json2pb
from portrayal_server.protobuf.ItemProfile_pb2 import ItemProfile, ItemBase
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TBufferedTransport

from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.interface.portrayal.ttypes import *

from set_logger import set_logger

cur_dir=os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
set_logger(cur_dir + "/logs/fun_test.log")


class Connection(object):
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.transport = TSocket.TSocket(ip, port)
        #self.transport.setTimeout(2000)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

    def connect(self):
        msg = "Connect must implement connect"
        raise  Exception(msg)

    def close(self):
        if self.transport:
            self.transport.close()

"""new server client connection class"""
class PortrayalConnection(Connection):
    def __init__(self, ip, port, name):
        super(PortrayalConnection, self).__init__(ip, port, name)

    def connect(self):
        self.__service = PortrayalService.Client(self.protocol)
        self.transport.open()
        if not self.__service:
            raise RuntimeError("Invalid Portrayal Thrift init params")

    def analyze_protobuf(self, request, modules):
        return self.__service.analyze_protobuf(request, modules)

#pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
#client = redis.Redis(connection_pool=pool)
client = PyBfdRedis.newClient('192.168.40.37:26379', 'Item')

rpc_con = PortrayalConnection("localhost", 10010, "Portayal")
rpc_con.connect()

def format(values):
    for key, value in values.items():
        if not value:
            del values[key]

def process(cid, iid):
    key_base = cid+'>'+iid+'>'+"ItemBase"
    try:
        #ib_res = client.get(key_base)
        ib_res = PyBfdRedis.get(client, key_base)
        ib = ItemBase()
        ib.ParseFromString(ib_res)
        if not ib.cid:
            return True
        result = rpc_con.analyze_protobuf(ib_res, None)
        if result.status == 0:
            item_profile = ItemProfile()
            item_profile.ParseFromString(result.value)
            profile_json_ = pb2json(item_profile)
            profile_json = json.loads(profile_json_)
            format(profile_json)
            logging.info(json.dumps(profile_json, ensure_ascii=False))
    except Exception as e:
        logging.error("process error key:%s  msg:%s" %(key_base, e))
        print("process error key:%s  msg:%s" %(key_base, e))
        return False


def read_data(file):
    fd = open(file)
    datas = []
    for value in fd.readlines():
        data = {}
        value_ = value.split('\t')
        #print(value_)
        data["cid"] = value_[0].replace("\n","")
        data["iid"] = value_[1].replace("\n","")
        datas.append(data)
    return datas

def main():
    datas = read_data("fun.txt")
    all_nums = len(datas)
    succeed_nums = 0
    for data in datas:
        if process(data["cid"],data["iid"]):
            succeed_nums = succeed_nums + 1
    logging.info("all_nums:%s, succeed_nums:%s" %(all_nums, succeed_nums))
    print("all_nums:%s, succeed_nums:%s" %(all_nums, succeed_nums))

main()
