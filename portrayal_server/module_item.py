class ModuleItem(object):

    def __init__(self, type, path, name, enable):
        self.type = type
        self.path = path
        self.name = name
        self.enable = enable


class ThriftModuleItem(ModuleItem):

    def __init__(self, type, path, name, is_enable, ip, port):
        super(ThriftModuleItem, self).__init__(type, path, name, is_enable)
        self.ip = ip
        self.port = port
