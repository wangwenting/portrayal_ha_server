import os
import sys
import threading
import time
from portrayal_server.config_parser import ConfigParser
from portrayal_server.common import log

LOG = log.getLogger()


def _normalize_filename(filename):
    if filename is not None:
        if filename.endswith('.pyc') or filename.endswith('.pyo'):
            filename = filename[:-1]
        elif filename.endswith('$py.class'):
            filename = filename[:-9] + '.py'
    return filename


class ModuleMonitor(threading.Thread):
    """
    mtimes: record all the file modify time(resources file and config file)
    interval: second
    module_manger: change module object when resources file changed or config file changed
    """
    def __init__(self, module_manager, interval=5):
        threading.Thread.__init__(self)
        self.daemon = True
        self.mtimes = {}
        self.interval = interval
        self.module_manager = module_manager
        self.module_files_ = module_manager.module_files_
        self.module_resources_ = module_manager.module_resources_
        self.modules_ = module_manager.modules_
        self.module_lines_ = module_manager.module_lines_
        self.updates = []

    def run(self):
        while True:
            #LOG.debug("current has load modules: %s" % self.modules_.keys())
            #LOG.debug("current module lines: %s" % self.module_lines_.keys())
            #LOG.debug("current module config parse:%s" % self.module_manager.config_parse)
            # self.module_code_scan()
            self.module_resource_scan()
            self.modules_config_scan()
            # print(self.mtimes)
            time.sleep(self.interval)

    def file_status(self, module_files):
        self.updates = []
        for key, file_names in module_files.items():
            # We're only interested in the source .py files
            for filename in file_names:
                filename = _normalize_filename(filename)

                # stat() the file.  This might fail if the module is part of a
                # bundle (.egg).  We simply skip those modules because they're
                # not really reloadable anyway.
                try:
                    stat = os.stat(filename)
                except OSError:
                    continue

                # Check the modification time.  We need to adjust on Windows.
                mtime = stat.st_mtime
                # Check if we've seen this file before.  We don't need to do
                # anything for new files.
                if filename in self.mtimes:
                    # If this file's mtime has changed, queue it for reload.
                    if mtime != self.mtimes[filename]:
                        if key not in self.updates:
                            self.updates.append(key)
                        LOG.info("module:%s, filename:%s changed" % (key, filename))
                # Record this filename's current mtime.
                self.mtimes[filename] = mtime

    def module_resource_scan(self):
        self.file_status(self.module_resources_)
        for update in self.updates:
            try:
                LOG.info("module:%s resource start update" % update)
                module_name = self.modules_[update].name
                class_name = self.modules_[update].class_name
                module_class = getattr(sys.modules[module_name], class_name)
                temp_module = module_class(self.module_manager.context)
                self.update_module(temp_module, update)
                self.modules_[update] = temp_module
                LOG.info("module:%s resource update end" % update)
            except Exception as e:
                LOG.error("module:%s resource update failed" % update)
        self.updates = []

    def module_code_scan(self):
        self.file_status(self.module_files_)

        for update in self.updates:
            run_module = self.modules_[update]
            module_class = self.module_manager.reload(run_module.path)
            temp_module = module_class(self.module_manager.context)
            self.update_module(temp_module, update)
            module_ = sys.modules[temp_module.name]
            filenames_ = []
            depends = self.module_manager.get_dependencies(module_.__name__)
            filenames_.append(module_.__file__)
            for depend in depends:
                filenames_.append(depend.__file__)
            self.module_manager.module_files_[update] = filenames_

            self.modules_[update] = temp_module

        self.updates = []

    def modules_config_scan(self):
        try:
            filename = self.module_manager.modules_config_path
            stat = os.stat(filename)
            mtime = stat.st_mtime
            if filename in self.mtimes:
                if mtime != self.mtimes[filename]:
                    self.update_manage(filename)
            self.mtimes[filename] = mtime
        except Exception as e:
            LOG.error("modules config update module field msg: %s" % e)
            self.mtimes[filename] = mtime
        self.updates = []

    def update_manage(self, filename):
        LOG.info("module config file changed")
        config_parse = ConfigParser()
        if not config_parse.parse_data():
            raise Exception("The module config is not regular, please change the file %s" % filename)
        # add module and modify the module property
        for key, module in config_parse.modules.items():
            if key not in self.module_manager.config_parse.modules:
                self.module_manager.module_add(key, module)
                continue
            if config_parse.modules[key].enable != self.module_manager.config_parse.modules[key].enable:
                LOG.info("module : %s changed status to %s from %s" %
                         (key, config_parse.modules[key].enable, self.module_manager.config_parse.modules[key].enable))
                self.module_manager.modules_[key].set_enable(config_parse.modules[key].enable)
        # delete module
        for key, module in self.module_manager.config_parse.modules.items():
            if key not in config_parse.modules:
                LOG.info("module: %s has been deleted" % key)
                del(self.module_manager.module_files_[key])
                del(self.module_manager.modules_[key])
                del(self.module_manager.module_resources_[key])
        # add and modify module lines
        for key, module_line in config_parse.module_lines.items():
            # new module_line add
            if key not in self.module_manager.config_parse.module_lines:
                LOG.info("add a module line:%s" % key)
                self.module_manager.module_line_add(key, module_line)
                continue
            # module_line changed
            if "%s" % module_line != "%s" % self.module_manager.config_parse.module_lines[key]:
                del(self.module_manager.module_lines_[key])
                LOG.info("module line:%s changed, value:%s" % (key, module_line))
                self.module_manager.module_line_add(key, module_line)
        self.module_manager.config_parse = config_parse

    def update_module(self, module, key):
        module.set_name(self.modules_[key].name)
        module.set_type(self.modules_[key].type)
        module.set_path(self.modules_[key].path)
        module.set_enable(self.modules_[key].enable)
        module.set_class_name(self.modules_[key].class_name)
        module.set_load_enable(self.modules_[key].load_enable)
        if module.type == "thrift":
            module.set_ip(self.modules_[key].ip)
            module.set_port(self.modules_[key].port)
