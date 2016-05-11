import PyBfdRedis
import json
import cPickle


#from  cost_tracker import TimeTracker
from ItemProfile_pb2 import ItemBase, ItemProfile
from pbjson import pb2dict, pb2json

client = PyBfdRedis.newClient('192.168.40.37:26379', 'Item')

out_datas = []

def process(cid, iid):
    global out_datas
    key_base = cid+'>'+iid+'>'+"ItemBase"
    key_file= cid+'>'+iid+'>'+"ItemProfile"

    try:
        data = {}
        ib_res = PyBfdRedis.get(client, key_base)
        ip_res = PyBfdRedis.get(client, key_file)
        ib = ItemBase()
        ib.ParseFromString(ib_res)
        ip = ItemProfile()
        ip.ParseFromString(ip_res)
        if not ib.cid:
            return True
        data["cid"] = cid
        data["iid"] = iid
        data["ib_res"] = ib_res
        data["ip_res"] = ip_res
        out_datas.append(data)
         
    except Exception as e:                                                                                                                        
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
    global out_datas
    datas = read_data("fun.txt")
    outfd = open("data.out","w")
    all_nums = len(datas)
    succeed_nums = 0
    for data in datas:
        process(data["cid"],data["iid"])
    print("start dump data")
    cPickle.dump(out_datas,outfd)
    outfd.close()

main()
