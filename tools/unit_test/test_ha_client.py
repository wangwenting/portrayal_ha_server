# -*- coding: utf-8 -*-
import traceback
import json

from thrift.transport import TSocket

from portrayal_server.interface.portrayal import PortrayalService
from portrayal_server.interface.portrayal.ttypes import *


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

if __name__ == "__main__":
    con = PortrayalConnection("localhost", 10010, "Portayal")
    try:
        con.connect()
    except Exception as e:
        traceback.print_exc()

    #json_request["modules"] =["age"]
    for i in range(1):
        file = con.analyze_json(json.dumps(u"西安瑞祥招待所"), None)
        print(file)
