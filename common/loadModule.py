#! /usr/bin/env python
#coding=utf-8
import string
import os
import sys
import imp
import time
#格式:GLOBAL_MODULE_CONFDICS={'模块名1':(时间戳,模块句柄),'模块名2':(时间戳,模块句柄)}
GLOBAL_MODULE_CONFDICS = {}


def load_module(module_name):
    global GLOBAL_MODULE_CONFDICS
    module_info_dic = {}
    mtime=0
    __module = None
    if module_name in GLOBAL_MODULE_CONFDICS:
        module_loadtime = GLOBAL_MODULE_CONFDICS[module_name][0]
        target_module = sys.modules[module_name]
        target_module_path = target_module.__file__
        if target_module_path[-4:] in ('.pyc', '.pyo', '.pyd'):
            target_module_path = target_module_path[:-1] # get the '.py' file
        mtime = os.path.getmtime(target_module_path)
        if mtime > module_loadtime:
            __module = reload(target_module)
            GLOBAL_MODULE_CONFDICS[module_name] = (mtime,__module)
        else:
            __module = GLOBAL_MODULE_CONFDICS[module_name][1]
    else:
        __module = __import__(module_name)
        name_list = module_name.split(".")
        name_list.pop(0)
        for name in name_list:
            __module = getattr(__module, name)
        GLOBAL_MODULE_CONFDICS[module_name] = (time.time(),__module)
    return __module


