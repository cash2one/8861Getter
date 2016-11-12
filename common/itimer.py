#!/usr/bin/env python
#coding=utf-8

'''
timer interface
'''

import time

g_timer_dict = {}

class iTimer(object):
    def __init__(self):
        self._itimer_dict = {}

    def _key(self, name):
        return "TM_%s" % (name)



    def start(self, name):
        key = self._key(name)
        self._itimer_dict[key] = {}
        self._itimer_dict[key]["start"]=self._itimer_dict[key]["end"]= time.time()

    def end(self, name):
        key = self._key(name)
        if key in self._itimer_dict:
            self._itimer_dict[key]["end"]= time.time()




    def _get_used_time(self, start_time, end_time):
        escape = (end_time - start_time) * 1000
        return str(escape)

    def escapeTime(self, name):
        key = self._key(name)
        if key in self._itimer_dict:
            return self._get_used_time(self._itimer_dict[key]["start"], self._itimer_dict[key]["end"])
        return 0

    def escapeTimes(self):
        _t_map = {}
        for (k, v) in self._itimer_dict.items():
            escape = self._get_used_time(v["start"], v["end"])
            _t_map[k] = escape
        return _t_map

    def clear(self):
        self._itimer_dict.clear()

    def __del__(self):
        self.clear()
