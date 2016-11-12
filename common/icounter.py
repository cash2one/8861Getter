#!/usr/bin/env python
#coding=utf-8

'''
counter interface
'''


class iCounter(object):
    def __init__(self):
        self._counter_dict = {}

    def _key(self, name):
        return ("CNT_%s") % (name)

    def incr(self, name, number=1):
        key = self._key(name)
        if key not in self._counter_dict:
            self._counter_dict[key] = number
        else:
            self._counter_dict[key] += number

    def getCnt(self, name):
        key = self._key(name)
        if key in self._counter_dict:
            return  self._counter_dict[key]
        return 0

    def getCnts(self):
        return self._counter_dict

    def clear(self):
        self._counter_dict.clear()

    def __del__(self):
        self.clear()