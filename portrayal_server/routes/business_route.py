# -*- coding: utf-8 -*-
import traceback

from portrayal_server.common import log
from route import Route

LOG = log.getLogger()

class BusinessRoute(Route):

    def __init__(self, context):
        super(BusinessRoute, self).__init__(context)

    def process(self, jsonbase):
        return "films"
