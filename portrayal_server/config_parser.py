# -*- coding: utf-8 -*-
import traceback
from oslo.config import cfg

from portrayal_server.common import log
from portrayal_server.module_item import ModuleItem, ThriftModuleItem
from portrayal_server.common.module_options import ModuleOptions

module_map = [
    cfg.StrOpt('modules_config_path',
               default="/etc/portrayal_server/modules.json",
               help="contain all the module lines resource "),
]
CONF = cfg.CONF
LOG = log.getLogger()
CONF.register_opts(module_map)


class ConfigParser(object):

    def __init__(self):
        """
        modules: {"age":{"type":"python", "path":"portrayal_server.modules.age_.age.Age", "enable":true}}
        module_lines = {"default":["age", "gender"],"film":["age"]}
        """
        self.modules = {}
        self.module_lines = {}
        self._modules_config_path = CONF.modules_config_path

    def __str__(self):
        return "modules:%s, module_lines:%s" % (self.modules.keys(), self.module_lines)

    @property
    def modules_config_path(self):
        return self._modules_config_path

    @staticmethod
    def get_modules(modules):
        modules_ = {}
        for key, value in modules.items():
            try:
                module_type = value["type"]
                path = value["path"]
                enable = value["enable"]
                name = key
                if module_type == "python" or module_type == "py":
                    module = ModuleItem(module_type, path, name, enable)
                elif module_type == "thrift":
                    ip = value["ip"]
                    port = value["port"]
                    module = ThriftModuleItem(module_type, path, name, enable, ip, port)
                modules_[name] = module
            except Exception as e:
                LOG.warning("Exception to Get module:%s. message:%s" % (key, e))
                continue
        return modules_

    def data_valid(self):
        """
        check all the module in _module_lines is exist in modules
        """
        modules = []
        for key, value in self.module_lines.items():
            modules.extend(value)
        for module in modules:
            if module in self.modules:
                continue
            else:
                LOG.error("module: %s not config, please config for it" % module)
                return False
        return True

    def parse_data(self):
        options = ModuleOptions()
        data = options.get_configuration(self._modules_config_path)
        self.module_lines = data.get("module_lines", None)
        modules = data.get("modules", None)
        self.modules = ConfigParser.get_modules(modules)

        if not self.modules:
            return False
        return self.data_valid()