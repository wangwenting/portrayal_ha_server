# -*- coding: utf-8 -*-

import os
import json
from oslo.config import cfg

from portrayal_server.common import log

LOG = log.getLogger()

modules_opts = [
    cfg.StrOpt('modules_json_config_location',
               default='/etc/portrayal_server/portrayal_server.conf',
               help='Absolute path to modules configuration JSON file.'),
]

CONF = cfg.CONF
CONF.register_opts(modules_opts)


class ModuleOptions(object):
    """
    load json file return dict data
    if file modify time not changed, direct return data
    """
    def __init__(self):
        super(ModuleOptions, self).__init__()
        self.data = {}
        self.last_modified = None

    @staticmethod
    def _get_file_handle(filename):
        """Get file handle. Broken out for testing."""
        return open(filename)

    @staticmethod
    def _get_file_timestamp(filename):
        """Get the last modified datetime. Broken out for testing."""
        try:
            return os.path.getmtime(filename)
        except os.error as e:
            LOG.debug("Could not stat modules options file %(filename)s: \
                      '%(e)s'", {'filename': filename, 'e': e})

    @staticmethod
    def _load_file(handle):
        """Decode the JSON file. Broken out for testing."""
        try:
            return json.load(handle)
        except ValueError as e:
            LOG.exception("Could not decode modules options: %s" % e)
            return {}

    def get_configuration(self, filename=None):
        """Check the json file for changes and load it if needed."""
        if not filename:
            filename = CONF.modules_json_config_location
        if not filename:
            return self.data
        last_modified = self._get_file_timestamp(filename)
        if (not last_modified or not self.last_modified or
                last_modified != self.last_modified):
            self.data = self._load_file(self._get_file_handle(filename))
            self.last_modified = last_modified
        if not self.data:
            self.data = {}

        return self.data
