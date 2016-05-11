# -*- coding: utf-8 -*-
import traceback
from oslo.config import cfg

from portrayal_server.module_manage import ModuleManage
from portrayal_server.common import log

CONF = cfg.CONF

if __name__ == "__main__":
    try:
        context = {}
        log.setup()
        manage_obj = ModuleManage(context)
        manage_obj.init_modules()
        print(manage_obj.modules_)
        print(manage_obj.modulelines_)
          
        process = manage_obj.get_module_line("default")
        json_base = {}
        json_file ={"modules":[]}
        if process:
            for pro in process:
                if pro.enable and pro.load_enable:
                    pro(json_base, json_file)
        print(json_file)
    except Exception as e:
        print(traceback.print_exc())
        log.getLogger().exception(e)


