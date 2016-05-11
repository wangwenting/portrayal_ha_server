import PyBfdRedis
import os
import traceback
import logging
import json
import redis
import multiprocessing
import time


from  cost_tracker import TimeTracker
from portrayal_server.protobuf.pbjson import pb2json, json2pb
from portrayal_server.protobuf.ItemProfile_pb2 import ItemProfile, ItemBase
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TBufferedTransport

from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.interface.portrayal.ttypes import *

from set_logger import set_logger

cur_dir=os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
set_logger(cur_dir + "/logs/stress_test.log")


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


pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
client = None


def init():
    global client
    client = redis.Redis(connection_pool=pool)
    print("init succeed")

def process(num,l, client, process_id):
    count = 0
    err_count = 0
    time_tracker = TimeTracker()
    rpc_con = PortrayalConnection("localhost", 10099, "Portayal")
    rpc_con.connect()
    pid = os.getpid()
    set_logger("%s/logs/stress_test_%s.log" %(cur_dir, pid))

    while True:
        if num.value >= 100000:
            break
        key_base ="Cjinshan>b1a4ee97f6b51c4f702948a9a1a303bd>ItemBase"
        try:
            ib_res = client.get(key_base)
            ib = ItemBase()
            ib.ParseFromString(ib_res)
            if not ib.cid:
                continue
        except Exception as e:
            print("get redis data key:%s  error:%s" % (key_base, e))
            continue
        l.acquire()
        num.value = num.value + 1
        l.release()
        count = count + 1
        time_tracker.start_tracker()
        try:
            result = rpc_con.analyze_protobuf(ib_res, None)
            #print("process_id:%s, count:%s" %(process_id, count))
        except Exception as e:
            err_count = err_count + 1
            print("get rpc server data key:%s error:%s" %(key_base, e))
        time_tracker.end_tracker()
        time_tracker.time_elapsed()
        time_tracker.inc_job_counter(1)
        job_count = time_tracker.get_job_count()
        if job_count % 1000 == 0:
            module_path = result.modules_path
            ip = ItemProfile()
            ip.ParseFromString(result.value)
            ip_ = pb2json(ip)
            ip_json = json.loads(ip_)
            print(module_path)
            
            logging.info("avg_time:%s, request_num:%s, all_time:%s, err_count:%s thread_id:%s" % (time_tracker.average_time_cost(),
                  job_count, time_tracker.get_time_elapsed(), err_count, os.getpid()))
    avg_time = time_tracker.average_time_cost()
    request_num = time_tracker.get_job_count()
    all_time = time_tracker.get_time_elapsed()
    print("avg_time:%s, request_num:%s, all_time:%s, err_count:%s" % (avg_time, request_num, all_time, err_count))

def main(thread_counts):
    global client
    num = multiprocessing.Value('d', 0.0)
    lock = multiprocessing.Lock()
    init()
    jobs = []
    all_time_start = time.time()
    for i in range(thread_counts):
        p = multiprocessing.Process(target=process, args=(num, lock, client, i))
        jobs.append(p)
        p.start()
    for job in jobs:
        job.join()
    all_time_end = time.time()
    print("num-value:%s all-time:%s" % (num.value, all_time_end-all_time_start))
main(24)
