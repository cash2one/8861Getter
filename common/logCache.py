#!/usr/bin/env python
#coding=utf-8

'''
log interface
'''

import itimer
import icounter
from kv import KV

class noLoggerInstance(Exception):
    pass


class noticeCache(object):

    def __init__(self):
        self._kv = KV()
        self._timer = itimer.iTimer()
        self._counter = icounter.iCounter()

    def startTimer(self, name):
        self._timer.start(name)

    def endTimer(self, name):
        self._timer.end(name)

    def incrCounter(self, name):
        self._counter.incr(name)

    def pushNotice(self, k ,v):
        self._kv.add(k, v)

    def timeEscape(self, name):
        return self._timer.escapeTime(name)

    def buildNotice(self, ft=0):
        self._kv.update(self._timer.escapeTimes())
        self._kv.update(self._counter.getCnts())
        if 0 == ft:
            log_msg = str(self._kv)
        else:
            log_msg = self._kv.genStr()
        self.clear()
        return log_msg

    def clear(self):
        self._kv.clear()
        self._counter.clear()
        self._timer.clear()

