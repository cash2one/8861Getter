#!/usr/bin/env python
#coding=utf-8

'''
kv interface
'''


class KV(object):
    def __init__(self):
        self._kv_dict = {}

    def add(self, k, v):
        self._kv_dict[k] = v

    def update(self, kv):
        self._kv_dict.update(kv)

    def __str__(self):
        kvStr = ""
        for k in self._kv_dict:
            v = self._kv_dict[k]
            kvStr += (" %s=%s") % (str(k), str(v))
        return  kvStr

    def genStr(self):
        kvStr = ""
        for k in self._kv_dict:
            v = self._kv_dict[k]
            kvStr += "%s [%s] " % (str(k), str(v))
        return kvStr


    def clear(self):
        self._kv_dict.clear()

    def __del__(self):
        self.clear()

if "__main__" == __name__:
    kv = KV()
    kv.add('zz', 'zz')
    kv.add('bb', 'bb')
    kv.add('ww', 'ww')

    d = {
        'z': 'z',
        'b': 'b',
        'c': 'c',
        'zz': 'wz'
    }

    kv.update(d)

    print kv