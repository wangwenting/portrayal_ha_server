# -*- coding: utf-8 -*-
import sys, traceback
import time, os

import Ice
Ice.loadSlice(os.path.dirname(os.path.abspath(__file__)) + '/WordSegmenter.ice')
import bfd

class Segmenter(object):
    def __init__(self, address = "WordSegmenter:tcp -h bgsbtsp0074-dqf -p 10020"):
        self.init(address)

    def init(self, address = "WordSegmenter:tcp -h bgsbtsp0074-dqf -p 10020"):
        self.ic = None
        self.segmenter = None
        try:
            self.ic = Ice.initialize(sys.argv)
            base = self.ic.stringToProxy(address)
            self.segmenter = bfd.WordSegmenterPrx.checkedCast(base)
            if not self.segmenter:
                raise RuntimeError("Invalid proxy")
        except:
            traceback.print_exc()
    
    def segment(self, text):
        try:
            result = self.segmenter.Segment(text)
        except Ice.Exception, e:
            self.cleanup()
            self.init()
            result = segmenter.Segment(text)
        return result[1]
        
    def cleanup(self):
        if self.ic:
            # Clean up
            try:
                self.ic.destroy()
            except:
                traceback.print_exc()
''' 
    
port = 10021
    
import sys
sys.path.append('./gen-py')

from wordseg import WordSeg
from wordseg.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class Segmenter(object):
    def __init__(self):
        self.init()

    def init(self):
        self.transport = TSocket.TSocket("bjlg-solr-8", port)
        self.transport.open()
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = WordSeg.Client(protocol)

    def segment(self, text):
        if type(text) is unicode:
            text = text.encode('utf-8')
        try:
            result = self.client.segment(text)
        except:
            self.init()
            result = self.client.segment(text)

        return result

    def cleanup(self):
        self.transport.close()

'''

if __name__ == '__main__':
    segmenter = Segmenter()
    for i in range(1000):
        results = segmenter.segment(u'大家电')
    for r in results: print r
    segmenter.cleanup()
