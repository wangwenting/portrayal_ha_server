# -*- coding: utf-8 -*-
class Route(object):
    def __init__(self, context):
        self.context_ = context

    '''the path which util.import_class'''
    def set_path(self, path):
        self.path_ = path

    def set_moudle_name(self, module):
        self.module_name_ = module

    def set_file_path(self, file_path):
        self.file_path_ = file_path

    def process(self):
        pass
