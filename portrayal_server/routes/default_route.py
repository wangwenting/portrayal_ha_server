# -*- coding: utf-8 -*-
from route import Route
from portrayal_server.zk_config.zk_client import zk_conf


class DefaultRoute(Route):

    DEFAULT = "default"

    def __init__(self, context):
        super(DefaultRoute, self).__init__(context)

    @staticmethod
    def get_module_names(modules, json_base):
        """
        :param modules: ["age", "gender"]
        :param json_base: {"cid":"Cjinshan", "iid":"123456"} json object
        :return: if modules not null, direct return, else by zk
        """
        if not modules:
            modules = []
            config = zk_conf.get_client(json_base["cid"])
            if config and "properties" in config:
                modules.extend(config["properties"])
        return modules

    def process(self, jsonbase):
        return self.DEFAULT
