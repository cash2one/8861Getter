#!/usr/bin/env python
#coding=utf-8
import os
import sys
import Queue
import signal
import time
import threading
# import magic
from optparse import OptionParser
pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append('%s/..' % (pwd))

from common import ilog
# from common import redisTalker
from common import util
from common import logCache
from common import  mysqlTalker
from common import storager
from common import fileExt

log_conf = ("%s/../conf/download.log.conf") % (pwd)
# redis_conf = ("%s/../../conf/redis.conf") % (pwd)
ilog.init(log_conf, "spider1688", "spider1688Wf")
# redisTalker.init(util.load_ini_conf(redis_conf))
mysql_conf = ("%s/../conf/mysql.conf") % (pwd)
mysqlTalker.init(util.load_ini_conf(mysql_conf))

G_STOP_FLAG = False
G_STORAGE_BASE_PATH = '/Users/baidu/banmen/8861Getter/data'

def signal_handler(signum=0, e=0):
    ilog.wflogger.warning('Get the quit cmd. I am trying to kill myself.')
    global G_STOP_FLAG
    G_STOP_FLAG = True

class SchedualWorker(threading.Thread):    # 处理工作请求
    def __init__(self, workQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.max_try_times = 16
        self.cur_try_times = 0
        self.max_sleep_time = 60
        self.nc = logCache.noticeCache()

    def run(self):
        while not G_STOP_FLAG:
            try:
                left_cnt = self.workQueue.qsize()
                ilog.logger.info('[chedualWorker] %s url left to dispatch.' % (str(left_cnt)))
                if left_cnt > 5:
                    self.cur_try_times = 0
                    time.sleep(0.5)
                    continue
                else:
                    # 动态调整睡眠时间
                    if 0 == left_cnt:
                        self.cur_try_times += 1
                        if self.cur_try_times >= self.max_try_times:
                            sleep_time = 1.5 + (self.cur_try_times - self.max_try_times) / 10
                            if sleep_time > self.max_sleep_time:
                                sleep_time = self.max_sleep_time
                        else:
                            sleep_time = 0.5
                        ilog.logger.info('[schedualWorker] no url left to schedule.I\'m  going to sleep %ss' % (sleep_time))
                        time.sleep(sleep_time)
                    else:
                        self.cur_try_times = 0

                    self._get_more()
                    # time.sleep(0.5)
            except Queue.Full:
                ilog.wflogger.warning('[schedualWorker] queue is full.')
                time.sleep(2)


    def _get_more(self):

        nc = self.nc
        nc.startTimer('selector')
        sql = 'select url, urlmd5, pic_url from resource where status=0 ' \
              'or (status = 2 and failed_times<15) limit 50;'
        res = mysqlTalker.getInstance('spider').query(sql)
        nc.endTimer('selector')
        if not res:
            ilog.wflogger.warning('[schedualWorker] no more url info: %s' % (nc.buildNotice()))
            return

        nc.pushNotice('rawCnt', len(res))
        for _url_info_dict in res:
            self.workQueue.put(_url_info_dict)
        ilog.logger.info('[schedualWorker] _get_more info:%s' % (nc.buildNotice()))


class Downloader(threading.Thread):    # 处理工作请求
    def __init__(self, workQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.max_sleep_time = 30
        self.continued_sleep_times = 0
        self.workQueue = workQueue


    def run(self):
        while not G_STOP_FLAG:
            try:
                _url_info_dict = self.workQueue.get(False)
                self._download_pic(_url_info_dict)
                time.sleep(0.5)
            except Queue.Empty:
                self.continued_sleep_times += 1
                sleep_time = self.continued_sleep_times
                if sleep_time > self.max_sleep_time:
                    sleep_time = self.max_sleep_time
                ilog.logger.info('[DispatchWorker]no url to download.I\'m going to sleep %ss.' % sleep_time)
                time.sleep(sleep_time)

    def _get_heades(self, hasreferer=True):
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            # 'referer': self._url,
            'Accept': 'image/webp,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        return _headers

    def _download_pic(self, url_info_dict):
        nc = logCache.noticeCache()
        url = url_info_dict['url']
        urlmd5 = url_info_dict['urlmd5']
        pic_url = url_info_dict['pic_url']
        big_pic_url = pic_url.replace('220x220xz', '400x400')
        nc.pushNotice('url', url)
        nc.pushNotice('urlmd5', urlmd5)
        nc.pushNotice('pic_url', pic_url)
        nc.pushNotice('big_pic_url', big_pic_url)
        ext = pic_url.split('.')[-1]
        # 优先下载大的图片
        pic_content = self._download(big_pic_url)
        if pic_content:
            nc.pushNotice('status', 'big')

        else:
            # 大图片不行的话，下载小图片
            time.sleep(0.2)
            pic_content = self._download(pic_url)
            if pic_content:
                nc.pushNotice('status', 'small')
            else:
                nc.pushNotice('status', 'fail')

        sql = ''
        if pic_content:
            # mimetype = magic.from_buffer(pic_content, mime=True)
            # if mimetype:
            #     ext = mimetype.split("/")[-1]
            # else:
            #     ext = fileExt.data_ext(pic_content)
            path = storager.save(pic_content, type='img', ext=ext, base_url=G_STORAGE_BASE_PATH)
            nc.pushNotice('inner_path', path)
            sql = 'update resource set failed_times=0, status=1, inner_path="%s" where urlmd5="%s";' \
                  % (path, urlmd5)

        else:
            sql = 'update resource set status=2 , failed_times=failed_times+1 where urlmd5="%s";' % urlmd5

        mysqlTalker._getInstance('spider').execute(sql)
        ilog.logger.info(nc.buildNotice())

    def _download(self, url):
        ret = None
        r = util.requests_ex(url, headers=self._get_heades())
        if not r:
            ilog.wflogger.warning('Downloader::_download %s failed.return None.' % url)
            return ret
        if r.status_code / 100 == 2:
            ret = r.content
        else:
            ilog.wflogger.warning('Downloader::_download %s failed.status_code=%s' % (url, r.status_code))
        return ret


class WorkManager(object):    # 线程池管理,创建
    def __init__(self):
        self.workQueue = Queue.Queue()  # 低优先级请求队列
        self.workers = []
        self._downloader_num = 1
        self._recruitThreads()


    def _recruitThreads(self):

        for i in range(self._downloader_num):
            worker = Downloader(workQueue=self.workQueue)    # 创建工作线程
            worker.setDaemon(True)
            self.workers.append(worker)    # 加入到线程队列

        # 低优先级调度线程
        worker = SchedualWorker(self.workQueue)
        worker.setDaemon(True)
        self.workers.append(worker)


    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()    # 从池中取出一个线程处理请求
            # worker.join()
            if worker.isAlive():
                self.workers.append(worker)    # 重新加入线程池中
        ilog.wflogger.warning('All jobs are completed.')


def main():
    reload(sys)
    sys.setdefaultencoding('utf8')
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    wm = WorkManager()
    wm.start()
    wm.wait_for_complete()

if __name__ == '__main__':
    main()
