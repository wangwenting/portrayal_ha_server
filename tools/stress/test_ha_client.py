#import PyBfdRedis
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
from bfd.harpc import client
from bfd.harpc.common import config
from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.interface.portrayal.ttypes import *

from set_logger import set_logger

cur_dir=os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
set_logger(cur_dir + "/logs/stress_test.log")


pool = redis.ConnectionPool(host='172.18.1.101', port=6379, db=0)
redis_client = None


def init():
    global redis_client
    redis_client = redis.Redis(connection_pool=pool)
    print("init succeed")

def process(num,l, process_id, rpc_con):
    global redis_client
    count = 0
    err_count = 0
    time_tracker = TimeTracker()
    pid = os.getpid()
    set_logger("%s/logs/stress_test_%s.log" %(cur_dir, pid))

    while True:
        if num.value >= 1000:
            break
        key_base ="Cjinshan>b1a4ee97f6b51c4f702948a9a1a303bd>ItemBase"
        try:
            ib_res = redis_client.get(key_base)
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
    num = multiprocessing.Value('d', 0.0)
    lock = multiprocessing.Lock()
    init()
    jobs = []
    conf = config.Config("../etc/demo_client.conf")
    manager = client.Client(PortrayalService.Client, conf)
    proxy_client = manager.create_proxy()

    all_time_start = time.time()
    for i in range(thread_counts):
        p = multiprocessing.Process(target=process, args=(num, lock, i, proxy_client))
        jobs.append(p)
        p.start()
    for job in jobs:
        job.join()
    all_time_end = time.time()
    print("num-value:%s all-time:%s" % (num.value, all_time_end-all_time_start))
    manager.close()
main(24)
