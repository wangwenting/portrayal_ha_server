# -*- coding: utf-8 -*-

import signal
import json

from bfd.harpc import server
from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.modules.new_classifier.segment import Segmenter


portrayal_pro = None
zk_address = "172.18.1.22:2181,172.18.1.23:2181,172.18.1.24:2181"


def create_portrayal():
    global portrayal_pro
    portrayal_pro = Segmenter()


def setup_handlers():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


class PortrayalServiceHandler(object):

    def __init__(self):
        pass

    def analyze_json(self, request, modules):
        print("1111111111111")
        a = ["1", "2"]
        a = portrayal_pro.segment(u"hello world")
        print(a)
        return json.dumps(a)

    def analyze_protobuf(self, request, modules):
        return portrayal_pro.segment(u"hello world")


class PortrayalServiceRun(object):

    @staticmethod
    def run_service(port):
        ser = server.GeventProcessPoolThriftServer("PortrayalServer$ItemService", port, zk_address, "PortrayalServer",
        #ser = server.ProcessPoolThriftServer("PortrayalServer$ItemService", port, zk_address, "PortrayalServer",
                                             "PortrayalServer", PortrayalService.Processor,
                                             PortrayalServiceHandler())

        ser.set_post_fork_callback(create_portrayal)
        ser.set_num_process(1)
        #ser.set_num_workers(1)

        print("------------server start------------")
        ser.start()

if __name__ == "__main__":
    setup_handlers()
    PortrayalServiceRun.run_service("10010")
