#!/usr/bin/env python
# -*- coding=utf-8 -*-
########################################################################
#
# Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
#
########################################################################

"""
File: util.py

utility function tools

Author: zhaobinwen(zhaobinwen@baidu.com)
Date: 2016/05/11 20:41:08
"""
import hashlib
import time
import sys
import ConfigParser
import uuid
import traceback
import requests
import ilog

LOG_LEVEL = "DEBUG"
LOG_LEVEL_MAP = {"DEBUG":0, "INFO":1, "WARNING":2, "ERROR":3, "FAULT":4}

def log(str, level="INFO"):
    """print日志,可以通过重定向保存"""
    global LOG_LEVEL
    if level not in LOG_LEVEL_MAP:
        level = "INFO"
    if LOG_LEVEL not in  LOG_LEVEL_MAP:
        LOG_LEVEL = "INFO"
    if LOG_LEVEL_MAP[level] < LOG_LEVEL_MAP[LOG_LEVEL]:
        return
    # 获取当前时间
    cur_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print "[%s] %s: %s" % (cur_str, level, str)

def load_ini_conf(conf):
    confdict = {}
    config = ConfigParser.ConfigParser()
    config.read(conf)
    #返回所有的sections
    sections = config.sections()
    for sec in sections:
        confdict[sec] = dict(config.items(sec))
    return confdict

def md5(data):
    m = hashlib.md5()
    try:
        m.update(data)
        return m.hexdigest()
    except Exception as e:
        m.update(data.encode("utf-8"))
        return m.hexdigest()


def ELFHash(key):
    hash = 0
    x    = 0
    for i in range(len(key)):
      hash = (hash << 4) + ord(key[i])
      x = hash & 0xF0000000
      if x != 0:
        hash ^= (x >> 24)
        hash &= ~x
    return (hash & 0x7FFFFFFF)


def addslashes(s):
    d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\", "%":"%%"}
    return ''.join(d.get(c, c) for c in s)

def genLogId():
    return uuid.uuid4().get_hex()

def load_module(module_name):
    __module = __import__(module_name)
    name_list = module_name.split(".")
    name_list.pop(0)
    for name in name_list:
        __module = getattr(__module, name)
    return __module

def requests_ex(url, data=None, headers=None, params=None, cookies=None, proxies=None, timeout=100,
                verify=False, retry_times=3):
    """ Requests封装避免抛未知异常, 且支持超时重试
        Args:
            data: string, If None, get; then post
            headers: dict, 请求头部, 默认None
            cookies: dict, 请求cookies, 默认None
            proxies: dict, 请求使用代理, 默认None
            timeout: int, 持续未接收到数据的最大时间间隔. 默认100
            verify: bool, 请求认证, 默认False
            retry_times: int. 超时重试次数, 默认3
    """


    idx = 0
    while idx < retry_times:
        try:
            if data is not None:
                res = requests.post(url=url, data=data, headers=headers, params=params, timeout=timeout,
                                    proxies=proxies, verify=verify, cookies=cookies)
            else:
                res = requests.get(url=url, headers=headers, params=params, timeout=timeout, proxies=proxies,
                                   verify=verify, cookies=cookies)
            return res
        except requests.exceptions.ConnectionError:
            ilog.wflogger.warning("connection fail, url:%s" % url)
            idx += 1
            time.sleep(5.5)
        except requests.exceptions.Timeout:
            ilog.wflogger.warning("time out, url:%s" % url)
            idx += 1
            time.sleep(5.5)
        except Exception as e:
            ilog.wflogger.error('download url:%s fail.error:%s' % (url, traceback.format_exc()))
            return None