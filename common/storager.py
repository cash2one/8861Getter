#!/usr/bin/env python
# -*- coding=utf-8 -*-
########################################################################
#
# Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
#
########################################################################

'''
save the object data to a target file with
path = ${base_url}/${type}/$md5[8]/$md5[18]/$md5[28]/md5.${type}
Author: zhaobinwen(zhaobinwen@baidu.com)
Date: 2016/05/11 19:09:49
'''
import os
import util
G_BASE_URL = "/home/work/www/static/spider"

def _create_dir(dir):
    if not os.access(dir, os.R_OK):
        os.makedirs(dir)

def save(data, type="other", ext="unknown", base_url=""):
    """

    Args:
        data: to save object data
        type: object type
        type: object ext
        base_url: default ""

    Returns:
        path: the target saved path

    """
    if not data:
        return False
    if not base_url:
        base_url = G_BASE_URL
    if "" == ext:
        ext = type
    if isinstance(data, unicode):
        data = data.encode("utf-8")
    target_md5 = util.md5(data)
    dir = "%s/%s/%s/%s/%s" % (base_url, type, target_md5[8], target_md5[18], target_md5[28])
    _create_dir(dir)
    if "other" == ext or "unknown" == ext:
        path = "%s/%s" % (dir, target_md5)
    else:
        path = "%s/%s.%s" % (dir, target_md5, ext)
    #print path
    with open(path, "w") as handle:
        handle.write(data)
    return path

if "__main__" == __name__:
    print save("123456", "txt")
    with open("test.jpg") as handle:
        data = handle.read()
        print save(data, "jpg")
