#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import json
import threading
import traceback
from kazoo.client import KazooClient
from kazoo.protocol.states import EventType


class ZKConfig(object):

    def __init__(self, hosts=None, path='/bre/clients'):
        self.path_clients = path
        self.clients = {}
        self.lock = threading.Lock()
        self.hosts = hosts
        # self.init_connect(hosts)

    def load_zk_resource(self, hosts=None):
        if not hosts:
            hosts = "172.18.1.22:2181,172.18.1.23:2181,172.18.1.24:2181"
        if hosts == self.hosts and self.clients:
            return
        self.hosts = hosts
        self.init_connect(hosts)
        self.get_clients_from_zk()

    def init_connect(self, hosts):
        self.zk = KazooClient(hosts=hosts)
        self.zk.start()
        logging.info('connect to zk servers')

    def get_clients_from_zk(self):
        logging.info('get clients from zookeeper')
        client_list = self.zk.get_children(self.path_clients, watch=self.watch_clients)
        clients = {}
        for client in client_list:
            path_client = self.path_clients + "/" + client
            data = self.zk.get(path_client, watch=self.watch_client)
            if not data:
                continue
            try:
                data = data[0]
                clients[client] = json.loads(data)
            except Exception as e:
                logging.warn("cid: %s json parse failed: %s" % (client, e))

        self.lock.acquire()
        self.clients = clients
        self.lock.release()
        logging.info('finish getting clients from zookeeper')
        logging.info('load %d clients' % len(self.clients))

    def get_client(self, cid):
        config = None
        try:
            config = self.clients.get(cid, None)
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("zkclient: %s", e)
        return config

    def set_clients(self, clients):
        for client, data in clients.iteritems():
            try:
                data = json.dumps(data)
                self.set_client(client, data)
            except Exception, e:
                logging.error(traceback.print_exc())
                logging.error("%s\t%s", client, e)
        
    def set_client(self, client, data):
        """
            client: 
            data: json string
        """
        path = self.path_clients + "/" + client
        if not self.zk.exists(path):
            self.zk.ensure_path(path)
            logging.info("create new path: %s", path)
        self.lock.acquire()
        try:
            self.zk.set(path, data)
        except Exception, e:
            logging.error(traceback.print_exc())
            logging.error("%s\t%s", client, e)
        self.lock.release()

    def watch_client(self, event):
        path = event.path
        client = path.split("/")[-1]
        etype = event.type
        print path, etype
        if etype == EventType.CHANGED:
            logging.info("change client: %s" % client)
            data = self.zk.get(path, watch=self.watch_client)
            if not data:
                return 
            try:
                data = data[0]
                data = json.loads(data)
            except Exception, e:
                logging.error("update client %s error:%s" % (client, e))
            self.clients[client] = data
        elif etype == EventType.DELETED:
            logging.info("remove client %s", client)
            del self.clients[client]
    
    # @self.zk.ChildrenWatch(self.path_clients)
    def watch_clients(self, children):
        print "haha", children
        new_client_lst = self.zk.get_children(self.path_clients, watch=self.watch_clients)
        new_clients = set(new_client_lst)
        client_add = new_clients - set(self.clients.keys())
        for client in client_add:
            path = self.path_clients + "/" + client
            data = self.zk.get(path)[0]
            try:
                data = json.loads(data)
            except Exception as e:
                logging.error("%s" % e)
                continue
            self.lock.acquire()
            self.clients[client] = data
            self.lock.release()

    def cleanup(self):
        if self.zk:
            self.zk.stop()
            logging.info("stop connection to zk")

    def dump_file(self, filename):
        with open(filename, "w") as wfile:
            for cid, data in self.clients.iteritems():
                data = json.dumps(data, ensure_ascii=False).encode('u8')
                print >> wfile, "%s\t%s" % (cid, data)

    def load_from_file_json(self, filename):
        with open(filename, 'r') as rfile:
            for line in rfile:
                client, data = line.strip('\n').split('\t')
                self.clients[client] = json.loads(data)

    def upload_zk_from_file(self, filename):
        self.load_from_file_json(filename)
        self.set_clients(self.clients)

    def test(self):
        # dump to file
        # filename = "map_file"
        # self.dump_file(filename)
   
        # load file into zk
        # self.upload_zk_from_file(filename)
        
        # read client
        self.load_zk_resource()
        print self.get_client(u'Cjinshan')

        # check watch
        # while True:
    #    data = zkc.get_client_local('Cbenlai')
    #    print json.dumps(data, ensure_ascii=False)
    #    time.sleep(10)

        # self.cleanup()

zk_conf = ZKConfig()

if __name__ == '__main__':
    zk_conf.test()
