# -*- coding: utf-8 -*-
import traceback
from oslo.config import cfg
from portrayal_server.common import config_init
from portrayal_server.common import log
from portrayal_server.config_parser import ConfigParser

CONF = cfg.CONF


if __name__ == "__main__":
    try:
        config_init.parse_args(default_config_files=["../etc/portrayal_server/portrayal_server.conf"])
        log.setup()
        print(CONF.lines_name)
        conf_p = ConfigParser()
        is_parse = conf_p.parse_data()
        print(conf_p.modules)
        print(conf_p.module_lines)
        print(is_parse)
        print(CONF.lines_name)
    except Exception as e:
        print(traceback.print_exc())



