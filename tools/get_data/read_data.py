import cPickle


#from  cost_tracker import TimeTracker
from ItemProfile_pb2 import ItemBase, ItemProfile
from pbjson import pb2dict, pb2json


with open("data.out",'r') as f:
    datas = cPickle.load(f)
    print(len(datas))
    print(datas[0]["cid"])
    ib_res = datas[0]["ib_res"]
    ib = ItemBase()
    ib.ParseFromString(ib_res)
    print(ib.cid)

