# -*- coding: utf-8 -*-
import traceback
from oslo.config import cfg
import sys

from portrayal_server.common import log
from portrayal_server.config_parser import ConfigParser
from portrayal_server.common import utils
from portrayal_server.common import reloader

CONF = cfg.CONF
LOG = log.getLogger()


def reload_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    module = sys.modules[mod_str]
    reloader.reload(module)
    try:
        return getattr(sys.modules[mod_str], class_str)
    except AttributeError:
        raise ImportError('Class %s cannot be found (%s)' %
                          (class_str,
                           traceback.format_exception(*sys.exc_info())))


class ModuleManage(object):
    """
    modules_: all the module object, key is module_name, value is module object
              example:{"age":ageObject, "gender":"genderObject}
    module_lines_: all the lines of modules, keys is line name, values is some modules name
              example:{"default":["age","gender"]}
    module_files_: not use, for dynamic load module file when file mtime changed
    module_resources_: module resources file path, dynamic load file when file mtime changed
                       key is module name, value is module resources file path
    config_parse: config of modules and modules line.
    modules_config_path: the file of modules config
    """
    def __init__(self, context):
        self.modules_ = {}
        self.module_lines_ = {}
        self.module_files_ = {}
        self.module_resources_ = {}
        self.config_parse = None
        self.modules_config_path = None
        self.context = context
        self.init_modules()

    def module_add(self, key, module):
        """
        :param key: "age"
        :param module: "modules.age_.age.Age"
        :return: no return just add by self
        """
        LOG.info("start load module: %s" % key)
        file_names = []
        module_class = utils.import_class(module.path)
        module_obj = module_class(self.context)
        module_name = utils.get_module(module.path)
        class_name = utils.get_class(module.path)
        module_ = sys.modules[module_name]
        depends = reloader.get_dependencies(module_.__name__)
        file_names.append(module_.__file__)
        for depend in depends:
            file_names.append(depend.__file__)
        self.module_files_[module.name] = file_names
        if module_obj.resource_files:
            self.module_resources_[module.name] = module_obj.resource_files
        module_obj.set_name(module_name)
        module_obj.set_type(module.type)
        module_obj.set_path(module.path)
        module_obj.set_enable(module.enable)
        module_obj.set_class_name(class_name)
        module_obj.set_load_enable(True)
        if module.type == "thrift":
            module_obj.set_ip(module.ip)
            module_obj.set_port(module.port)

        self.modules_[key] = module_obj
        LOG.info("end load module: %s" % key)

    def module_line_add(self, key, module_line):
        self.module_lines_[key] = []
        for module in module_line:
            if module in self.modules_:
                self.module_lines_[key].append(module)
            else:
                LOG.exception("module_line:%s not load complete, module:%s not loaded" % (key, module))

    def init_modules(self):
        self.config_parse = ConfigParser()
        self.modules_config_path = self.config_parse.modules_config_path
        if not self.config_parse.parse_data():
            LOG.exception("The module config is not regular")
            raise Exception("The module config is not regular, please change the file %s" % self.modules_config_path)
        reloader.enable(["oslo.config", "portrayal_server.common"])
        for key, module in self.config_parse.modules.items():
            try:
                self.module_add(key, module)
            except Exception as e:
                LOG.exception("import module and create object error:%s exception:%s" % (key, e))
                continue

        for key, module_line_ in self.config_parse.module_lines.items():
            self.module_line_add(key, module_line_)

    def get_module_names(self, key):
        module_names = self.module_lines_.get(key, None)
        return module_names

    def get_modules(self, modules):
        app_modules = []
        for module in modules:
            if self.modules_.has_key(module):
                app_modules.append(self.modules_[module])
            else:
                LOG.warning("request module:%s not exist in modules" % module)
        return app_modules

    def get_module(self, module_name):
        module = self.modules_.get(module_name, None)
        if not module:
            LOG.warning("Module:%s doesn't exist" % module_name)
        return module

    @staticmethod
    def reload(path):
        return reload_class(path)

    @staticmethod
    def get_dependencies(module):
        return reloader.get_dependencies(module)