#!/usr/bin/env python
# coding:utf-8
"""redis 操作简单封装"""
import sys
import os
import redis
import time
import traceback
import util
import threadHelp
from common import ilog
g_db = {}
g_confdict = {}
class notExistRedisInstance(Exception):
    pass

class RedisTalker(object):
    """redis 简单封装"""
    def __init__(self, host, port, db=0, keyType="" , expire_time="", cache_ver =""):
        self.host = host
        self.port = port
        self.db = db
        self.keyType = keyType
        self.expire_time = expire_time
        self.cache_ver = cache_ver
        self.connect()

    def connect(self, retry_num=5):
        """ 连接数据库 """
        connect_flag = False
        for i in range(retry_num):
            if i != 0:
                # 等待一段时间再重试
                ilog.logger.debug("waiting 2 seconds...")
                time.sleep(2)
            try:
                self.conn = redis.Redis(host=self.host,
                                        port=self.port,
                                        db=self.db)
            except Exception as e:
                err_str = "can not connect to db(%d), err_msg[%s]" % (
                    i + 1, traceback.format_exc())
                ilog.wflogger.warning(err_str)
                continue
            connect_flag = True
            break
        if not connect_flag:
            err_str = "Error: fail to connect to db!"
            ilog.wflogger.error(err_str)
            #raise Exception(err_str)

    def _set(self, key, value):
        ilog.logger.debug("[%s:%s]set cache [%s:%s]" % (self.host, self.port, key, value))
        self.conn.set(key, value)
        if "" != self.expire_time:
            self.conn.expire(key, int(self.expire_time))

    def _key(self, key):
        k = self.keyType + "_" + str(key)
        if "" != self.cache_ver:
            k = k + "_" + self.cache_ver
        return  k

    def _get(self, key):
        v = self.conn.get(key)
        if not v:
            ilog.logger.debug("[%s:%s]%s not hit cache" % (self.host, self.port, key))
        else:
            ilog.logger.debug("[%s:%s]%s hit cache" % (self.host, self.port, key))
        return v

    def getKeyType(self):
        return self.keyType

    def getFullKeyType(self):
        return 'redis_%s' % (self.keyType)

    def set(self, key, value):
        k = self._key(key)
        try:
            self._set(k, value)
            return True
        except Exception as e:
            ilog.wflogger.error(e)
            ilog.logger.info("reconnecting db...")
            try:
                self.connect()
                self._set(k, value)
            except Exception as e:
                ilog.wflogger.warning(str(e))

    # 删除
    def _rm(self, key):
        ilog.logger.debug("[%s:%s] rm cache %s" % (self.host, self.port, key))
        return self.conn.delete(key)

    # 自增
    def _incr(self, key, default=1):
        ilog.logger.debug("[%s:%s] incr cache %s" % (self.host, self.port, key))
        if 1 == default:
            ret = self.conn.incr(key)
        else:
            ret = self.conn.incr(key, default)
        if "" != self.expire_time:
            self.conn.expire(key, int(self.expire_time))
        return ret

    # 自减
    def _decr(self, key, default=1):
        ilog.logger.debug("[%s:%s] decr cache %s" % (self.host, self.port, key))
        if 1 == default:
            ret = self.conn.decr(key)
        else:
            ret = self.conn.decr(key, default)
        if "" != self.expire_time:
            self.conn.expire(key, int(self.expire_time))
        return ret


    def rm(self, key):
        k = self._key(key)
        try:
            return self._rm(k)
        except Exception as e:
            ilog.wflogger.error(e)
            ilog.logger.debug("reconnecting db...")
            try:
                self.connect()
                return self._rm(k)
            except Exception as e:
                ilog.wflogger.warning(str(e))
                return None

    def incr(self, key, default=1):
        k = self._key(key)
        try:
            return self._incr(k, default)
        except Exception as e:
            ilog.wflogger.error(e)
            ilog.logger.debug("reconnecting db...")
            try:
                self.connect()
                return self._incr(k, default)
            except Exception as e:
                ilog.wflogger.warning(str(e))
                return None

    def decr(self, key, default=1):
        k = self._key(key)
        try:
            return self._decr(k, default)
        except Exception as e:
            ilog.wflogger.error(e)
            ilog.logger.debug("reconnecting db...")
            try:
                self.connect()
                return self._decr(k, default)
            except Exception as e:
                ilog.wflogger.warning(str(e))
                return None

    def get(self, key):
        k = self._key(key)
        try:
            return self._get(k)
        except Exception as e:
            ilog.wflogger.error(e)
            ilog.logger.debug("reconnecting db...")
            try:
                self.connect()
                return self._get(k)
            except Exception as e:
                ilog.wflogger.warning(str(e))
                return None

    def expire(self, key , expireTime):
        k = self._key(key)
        self.conn.expire(k, expireTime)


def init(confdict):
    global g_confdict
    g_confdict = confdict
    main_key = threadHelp.genKey()
    try:
        threadHelp.acquireLock()
        if main_key in g_db:
            g_db.pop(main_key)
        g_db[main_key] = {}
        for (key, subdict) in confdict.items():
            if 'global' == key:
                continue
            host = subdict.get('host', '')
            port = subdict.get('port', '')
            db = subdict.get('db', '')

            if '' == host:
                host = g_confdict['global'].get('host', '')

            if '' == port:
                port = g_confdict['global'].get('port', '')

            if '' == db:
                db = g_confdict['global'].get('db', '')

            g_db[main_key][key] = RedisTalker(host=host,
                                   port=int(port),
                                   db=int(db),
                                   keyType=subdict.get("key_type", ""),
                                   expire_time=subdict.get("expire", ""),
                                   cache_ver=subdict.get("cache_ver", "")
                                   )
    except Exception as e:
        pass
    finally:
        threadHelp.releaseLock()

def _getInstance(db):
    global g_confdict
    if db not in g_confdict:
        ilog.wflogger.warning("%s db does not exist." % (db))
        raise notExistRedisInstance
    subdict = g_confdict[db]

    host = subdict.get('host', '')
    port = subdict.get('port', '')
    db = subdict.get('db', '')

    if '' == host:
        host = g_confdict['global'].get('host', '')

    if '' == port:
        port = g_confdict['global'].get('port', '')

    if '' == db:
        db = g_confdict['global'].get('db', '')

    dbObj= RedisTalker(host=host,
                       port=int(port),
                       db=int(db),
                       keyType=subdict.get("key_type", ""),
                       expire_time=subdict.get("expire", ""),
                       cache_ver=subdict.get("cache_ver", "")
                       )
    return dbObj

def getInstance(db):
    main_key = threadHelp.genKey()
    if main_key not in g_db:
        try:
            threadHelp.acquireLock()
            g_db[main_key] = {}
        except Exception as e:
            pass
        finally:
            threadHelp.releaseLock()
    if db not in g_db[main_key]:
        dbObj = _getInstance(db)
        try:
            threadHelp.acquireLock()
            g_db[main_key][db] = dbObj
        except Exception as e:
            pass
        finally:
            threadHelp.releaseLock()
    return g_db[main_key][db]

# def init(confdict):
#     global g_confdict
#     g_confdict = confdict
#
# def getInstance(db):
#     if db not in g_confdict:
#         raise notExistRedisInstance
#     subdict = g_confdict[db]
#     return RedisTalker(host=subdict["host"],
#                             port=int(subdict["port"]),
#                             db=int(subdict["db"]),
#                             keyType=subdict.get("key_type", ""),
#                             expire_time=subdict.get("expire", ""),
#                             cache_ver=subdict.get("cache_ver", "")
#                             )


#    if db not in g_confdict:
#        raise notExistMysqlInstance
#    subdict = g_confdict[db]
#    db_obj = MysqlTalker(host=subdict["host"],
#                            port=subdict["port"],
#                            db=subdict["db"],
#                            user=subdict["user"],
#                            passwd=subdict["passwd"]
#                            )
#    return db_obj



if "__main__" == __name__:
    pwd = os.path.dirname(os.path.realpath(__file__))
    redis_conf = ("%s/../extractor/conf/redis.conf") % (pwd)
    init(util.load_ini_conf(redis_conf))
    getInstance("url").set("key1","value1")
    getInstance("pattern").set("key2","value2")
    print getInstance("url").get("key1")
    print getInstance("pattern").get("key2")
    getInstance("error")
