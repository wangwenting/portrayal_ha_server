# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
from logging.handlers import TimedRotatingFileHandler


def set_logger(filename):
    log = logging.getLogger()
    #formatter = logging.Formatter('%(name)-12s %(asctime)s level-%(levelname)-8s thread-%(thread)-8d %(message)s')
    fmt_str = '[%(levelname)s %(asctime)s @ %(process)d] - %(message)s'
    formatter = logging.Formatter(fmt_str)
    fileTimeHandler = TimedRotatingFileHandler(filename, "D", 1, 20)

    fileTimeHandler.suffix = "%Y%m%d"  #设置 切分后日志文件名的时间格式 默认 filename+"." + suffix 如果需要更改需要改logging 源码
    fileTimeHandler.setFormatter(formatter)
    logging.basicConfig(level = logging.INFO)
    log.handlers = []
    log.addHandler(fileTimeHandler)
    log.setLevel(logging.DEBUG)


def set_logger2(filename):
    logger = logging.getLogger()
    hdlr = logging.FileHandler(filename)
    fmt_str = '[%(levelname)s %(asctime)s @ %(process)d] - %(message)s'
    formatter = logging.Formatter(fmt_str)
    hdlr.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
