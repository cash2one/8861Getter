#!/usr/bin/env python
#coding=utf-8

'''
log interface
'''

import sys
import os
import logging
import logging.config
logger = None
wflogger = None
_g_is_init = False

class noLoggerInstance(Exception):
    pass

def init(config, default_info_logger, default_warn_logger):
    global _g_is_init
    global logger
    global wflogger
    if _g_is_init:
        return
    logging.config.fileConfig(config)
    logger = logging.getLogger(default_info_logger)
    if not logger:
        raise noLoggerInstance
    wflogger = logging.getLogger(default_warn_logger)
    if not wflogger:
        raise noLoggerInstance
    _g_is_init = True


def getLogger(name=''):
    global logger
    if '' == name:
        return logger
    _logger = logging.getLogger(name)
    if _logger:
        return _logger
    return logger
