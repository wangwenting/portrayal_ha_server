# -*- coding: utf-8 -*-
import json
import traceback
import sys
import time

from oslo.config import cfg

from portrayal_server.common import utils
from portrayal_server.common import log
from portrayal_server.interface.portrayal.ttypes import *
from portrayal_server.protobuf.pbjson import pb2json, json2pb
from portrayal_server.protobuf.ItemProfile_pb2 import ItemProfile as Profile
from portrayal_server.protobuf.ItemProfile_pb2 import ItemBase as Base
from portrayal_server.module_manage import ModuleManage
from portrayal_server.monitor import ModuleMonitor

pro_config = [
    cfg.StrOpt('route_path',
               default="portrayal_server.routes.default_route.DefaultRoute",
               help='the route which user can implement'),
]
CONF = cfg.CONF
LOG = log.getLogger()
CONF.register_opts(pro_config, group="route")


class PortrayalPro(object):
    """
    _route_path: route class module path
    route:
    manage: manage all the modules and module lines
    monitor: monitor all the module resource file and module config file
    context:
    """
    def __init__(self):
        self._route_path = CONF.route.route_path
        self.route = None
        self.context = None
        self.init_context()
        self.manage = ModuleManage(self.context)
        self.init_route(self.context)
        self.monitor = ModuleMonitor(self.manage)
        self.monitor.start()

    def init_context(self):
        self.context = None

    def init_route(self, context):
        LOG.info("init route:%s start" % self._route_path)
        class_route = utils.import_class(self._route_path)
        module_name = utils.get_module(self._route_path)
        module = sys.modules[module_name]
        self.route = class_route(context)
        self.route.set_path(self._route_path)
        self.route.set_moudle_name(module.__name__)
        self.route.set_file_path(module.__file__)
        LOG.info("init route:%s end" % self._route_path)

    def get_module_names(self, modules, json_base):
        modules_ = self.route.get_module_names(modules, json_base)
        if not modules_:
            module_line = self.route.process(json_base)
            modules_ = self.manage.get_module_names(module_line)
        return modules_

    def get_module(self, module_name):
        """
        :param module_name: "age"
        :return: age object
        """
        return self.manage.get_module(module_name)

    def process_js(self, json_result, request, modules):
        """
        :param json_result:  {"status":0, "err_msg":{"code":300001,"describe":""}, "value":""}
        :param request: json request string
        :param modules: ["age", "gender"]
        :return:
        """
        item_base = json.loads(request)
        profile = Profile()
        profile.cid = item_base["cid"]
        profile.iid = item_base["iid"]
        profile.creation_time = long(time.time())
        profile_ = pb2json(profile)
        item_profile = json.loads(profile_)
        modules_ = self.get_module_names(modules, item_base)
        for module_ in modules_:
            module_app = self.get_module(module_)
            ret = module_app(item_base, item_profile)
            json_result["modules_path"].append(module_)
            if ret["status"] != 0:
                json_result["status"] = ret["status"]
                json_result["err_msg"] = ret["err_msg"]
                break
        json_result["value"] = item_profile

    def process_pro(self, result, request, modules):
        item_base = json.loads(request)
        LOG.info("cid:%s, iid:%s request" % (item_base["cid"],item_base["iid"]))
        profile = Profile()
        profile.cid = item_base["cid"]
        profile.iid = item_base["iid"]
        profile.creation_time = long(time.time())
        profile_ = pb2json(profile)
        item_profile = json.loads(profile_)

        modules_ = self.get_module_names(modules, item_base)
        modules_path = []
        for module_ in modules_:
            module_app = self.get_module(module_)
            if not module_app:
                continue
            ret = module_app(item_base, item_profile)
            modules_path.append(module_)
            if ret["status"] != 0:
                result.status = ret["status"]
                err_msg = ErrMsg()
                err_msg.code = ret["err_msg"]["code"]
                err_msg.describe = ret["err_msg"]["describe"]
                result.msg = err_msg
                break
        result.modules_path = json.dumps(modules_path)
        result.value = json2pb(Profile, json.dumps(item_profile)).SerializeToString()

    def process_protobuf(self, request, modules):
        """
        :param request: protobuf string
        :param modules: '["age", "gender"]'
        :return:
        """
        result = Result()
        result.status = 1
        try:
            item_base = Base()
            item_base.ParseFromString(request)
            item_base_ = pb2json(item_base)
            if modules:
                modules = json.loads(modules)
            self.process_pro(result, item_base_, modules)
            if result.status == 1:
                result.status = 0
        except Exception as e:
            result.status = 1
            err_msg = ErrMsg()
            err_msg.code = 30000
            err_msg.describe = "request protobuf server error"
            result.msg = err_msg
            LOG.error("process_probuf error:%s" % e)
        return result

    def process_json(self, request, modules):
        """
        :param request: json string '["cid":Cjinshan", "iid":"123232"]'
        :param modules: '["age", "gender"]'
        :return:
        """
        try:
            json_result = {"modules_path": []}
            if modules:
                modules = json.loads(modules)
            self.process_js(json_result, request, modules)

            # if modules return no status, set default status
            status = json_result.get("status", None)
            if not status:
                json_result["status"] = 0

        except Exception as e:
            json_result["status"] = 1
            json_result["err_msg"] = {"code": 30000, "describe": "request protobuf server error"}
            LOG.error("process_josn error:%s" % e)
            traceback.print_exc()
        return json.dumps(json_result)
