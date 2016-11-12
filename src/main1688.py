#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os
import requests
import json
import sys
import Queue
import threading
from optparse import OptionParser
pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append('%s/..' % (pwd))
import subItemBuilder
import akindCrawl
from common import ilog
from common import mysqlTalker
from common import util

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

pwd = os.path.dirname(os.path.realpath(__file__))
log_conf = ("%s/../conf/log.conf") % (pwd)
redis_conf = ("%s/../conf/redis.conf") % (pwd)
mysql_conf = ("%s/../conf/mysql.conf") % (pwd)

ilog.init(log_conf, "spider1688", "spider1688Wf")
# redisTalker.init(util.load_ini_conf(redis_conf))
mysqlTalker.init(util.load_ini_conf(mysql_conf))

class Clawler(threading.Thread):
    def __init__(self, queue, cate, cookie_file):
        threading.Thread.__init__(self)
        self._queue = queue
        self._cookie_file = cookie_file
        self._cate = cate
        self.setDaemon(True)

    def run(self):
        while True:
            try:
                url = self._queue.get(False)
                if not url:
                    continue
                print url
                crawler = akindCrawl.AKindCrawler(url, self._cookie_file, self._cate)
                crawler.work()
            except Queue.Empty:
                break


def main(seed, cate, cookie_file, filter_feature_index_list, enable_price_filter, p_feature, p_url):
    sub_cate_builder = subItemBuilder.SubCateBuilder(seed, cate, cookie_file, filter_feature_index_list, enable_price_filter)
    if p_feature:
        sub_cate_builder.print_feature_info()
        sys.exit(0)
    if p_url:
        sub_cate_builder.print_sub_url_info()
        sys.exit(0)
    sub_cate_builder.print_feature_info(_to_screen=False)
    workQueue = Queue.Queue()  # 低优先级请求队列
    item_url_list = sub_cate_builder.get_sub_url_info()
    for url in item_url_list:
        workQueue.put(url)

    worker_num = 1
    workers = []

    for i in xrange(worker_num):
        worker = Clawler(workQueue, cate, cookie_file)
        worker.setDaemon(True)
        workers.append(worker)  # 加入到线程队列
    # 启动
    for w in workers:
        w.start()

    # 等待结束
    while len(workers):
        worker = workers.pop()  # 从池中取出一个线程处理请求
        # worker.join()
        if worker.isAlive():
            workers.append(worker)  # 重新加入线程池中

if "__main__" == __name__:
    parser = OptionParser()
    parser.add_option("--print_feature", dest="p_feature")
    parser.add_option("--print_url", dest="p_url")
    (options, args) = parser.parse_args()
    if not options.p_feature:
        p_feature = False
    else:
        p_feature = options.p_feature == 'yes'
    if not options.p_url:
        p_url = False
    else:
        p_url = options.p_url == 'yes'

    import conf._1688 as _1688Conf
    seed = _1688Conf.seed
    cookie_file = _1688Conf.cookie_file
    enable_price_filter = _1688Conf.enable_price_filter
    filter_feature_index_list = _1688Conf.filter_feature_index_list
    cate = _1688Conf.cate
    main(seed, cate, cookie_file, filter_feature_index_list, enable_price_filter, p_feature, p_url)
