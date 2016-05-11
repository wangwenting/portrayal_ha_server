# -*- coding: utf-8 -*-

import os
import signal

from oslo.config import cfg
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TProcessPoolServer
from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.portrayal_pro import PortrayalPro
from portrayal_server.common import log
from portrayal_server.common import config_init
from portrayal_server.zk_config.zk_client import zk_conf
from portrayal_server.modules.new_classifier.classifier import Category, ClassifierWrap, MyPipeline

ha_config = [
    cfg.StrOpt('zk_address',
               default="172.18.1.22:2181,172.18.1.23:2181,172.18.1.24:2181",
               help='the ha zk and category_mapping'),
]

server_config = [
    cfg.IntOpt('thrift_port',
               default="10010",
               help='thrift port'),

    cfg.IntOpt('thread_nums',
               default="1",
               help='thread nums'),
]

CONF = cfg.CONF
LOG = log.getLogger()
CONF.register_opts(ha_config, group="Ha")
CONF.register_opts(server_config)

portrayal_pro = None

def create_portrayal():
    global portrayal_pro
    log.setup("portrayal_server", os.getpid())
    portrayal_pro = PortrayalPro()


def setup_handlers():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


class PortrayalServiceHandler(object):

    def __init__(self):
        pass

    def analyze_json(self, request, modules):
        return portrayal_pro.process_json(request, modules)

    def analyze_protobuf(self, request, modules):
        return portrayal_pro.process_protobuf(request, modules)


class PortrayalServiceRun(object):

    @staticmethod
    def run_service(port):
        handler = PortrayalServiceHandler()
                                                                                                                                                     
        processor = PortrayalService.Processor(handler)
        transport = TSocket.TServerSocket(port=port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        #server = TServer.TThreadPoolServer(processor, transport,
        #                               tfactory, pfactory)
        server = TProcessPoolServer.TProcessPoolServer(processor, transport,
                                                       tfactory, pfactory)
        server.setPostForkCallback(create_portrayal)
        print "Thread Nums: %s" % CONF.thread_nums
        server.setNumWorkers(CONF.thread_nums)
        print("server start")                                                                                                                                         
        server.serve()  

if __name__ == "__main__":
    setup_handlers()
    config_init.parse_args(default_config_files=["/home/wenting/truck/python/portrayal_ha_server/etc/portrayal_server/portrayal_server.conf"])
    log.setup("portrayal_server")
    print "Zk address:%s" % CONF.Ha.zk_address
    #zk_conf.load_zk_resource(CONF.Ha.zk_address)
    PortrayalServiceRun.run_service(CONF.thrift_port)
