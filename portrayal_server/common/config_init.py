# -*- coding: utf-8 -*-

from oslo.config import cfg

CONF = cfg.CONF


def parse_args(args=None, usage=None, default_config_files=None, validate_default_values=False):
    CONF(args=args,
         project='portrayal_server',
         version='1.1.01',
         usage=usage,
         default_config_files=default_config_files,
         validate_default_values=validate_default_values)
