#!/usr/bin/env python
# coding:utf-8
"""mysql 操作简单封装"""
import os
import torndb
import time
import traceback
import util
import threadHelp
from common import ilog
from common import logCache
from common import global_conf as _gc
g_db = {}
g_confdict = {}
class notExistMysqlInstance(Exception):
    pass


class MysqlTalker(object):
    """mysql 操作简单封装"""
    def __init__(self, host, port, db, user, passwd, charset="utf8", connect_timeout=360):
        self.host = "%s:%s" % (host, port)
        self.db = db
        self.user = user
        self.passwd = passwd
        self.charset = charset
        self.connect_timeout = connect_timeout
        self.connect()

    def __del__(self):
        self.conn.close()

    def connect(self, retry_num=5):
        """ 连接数据库 """
        try:
            self.conn.close()
        except Exception as e:
            pass
        connect_flag = False
        for i in range(retry_num):
            if i != 0:
                # 等待一段时间再重试
                ilog.logger.info("waiting 2 seconds...")
                time.sleep(2)
            try:
                self.conn = torndb.Connection(
                    host= self.host,
                    user= self.user,
                    password=self.passwd,
                    database=self.db,
                    charset=self.charset,
                    connect_timeout=self.connect_timeout)
            except Exception as e:
                err_str = "can not connect to db(%d), err_msg[%s]" % (
                    i + 1, traceback.format_exc())
                ilog.wflogger.error(err_str)
                continue
            connect_flag = True
            break
        if not connect_flag:
            err_str = "Error: fail to connect to db!"
            ilog.wflogger.error(err_str)
            raise Exception(err_str)

    def _reconnect(self):
        self.conn.reconnect()


    def _stat(self, func):
        def _log(sql, *args, **kwargs):
            nc = logCache.noticeCache()
            nc.pushNotice('sql', sql)
            nc.pushNotice('host', self.host)
            nc.pushNotice('db', self.db)
            local_exception = None
            ret = None
            try:
                nc.startTimer('cost')
                ret = func(sql, *args, **kwargs)
            except Exception as e:
                local_exception = e
            finally:
                try:
                    if not local_exception:
                        nc.endTimer('cost')
                        _cost = nc.timeEscape('cost')
                        # if local_exception:
                        #     err_str = str(local_exception)
                        # else:
                        #     err_str = 'success'
                        # nc.pushNotice('error', err_str)
                        _nc_str = nc.buildNotice(ft=1)
                        ilog.getLogger('db').info(_nc_str)
                        if float(_cost) >= _gc.SLOW_SQL_TIME:
                            ilog.getLogger('dbWf').warning(_nc_str)
                except Exception as e:
                    pass
                if local_exception:
                    raise local_exception
            return ret
        return _log

    def _execute(self, sql):
        return self._stat(self.conn.execute)(sql)

    def _query(self, sql):
        return self._stat(self.conn.query)(sql)

    def _get(self, sql):
        return self._stat(self.conn.get)(sql)

    def execute(self, sql):
        """执行语句"""
        try:
            # self.conn.execute(sql)
            self._execute(sql)
        except Exception as e:
            ilog.logger.debug("failed excute sql:%s.traceback:%s)" % (sql, str(e)))
            self._reconnect()
            # self.conn.execute(sql)
            self._execute(sql)


    def query(self, sql):
        """获取一行或多行"""
        try:
            # response = self.conn.query(sql)
            response = self._query(sql)
        except Exception,e:
            ilog.logger.debug("failed excute sql:%s.traceback:%s)" % (sql, str(e)))
            self._reconnect()
            # response = self.conn.query(sql)
            response = self._query(sql)
        return response

    def get(self, sql):
        """获取一行"""
        try:
            # response = self.conn.get(sql)
            response = self._get(sql)
        except Exception,e:
            ilog.logger.debug("failed excute sql:%s.traceback:%s)" % (sql, str(e)))
            self._reconnect()
            # response = self.conn.get(sql)
            response = self._get(sql)
        return response

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

            g_db[main_key][key] = MysqlTalker(host=host,
                                   port=port,
                                   db=db,
                                   user=subdict["user"],
                                   passwd=subdict["passwd"]
                                   )
    except Exception as e:
        pass
    finally:
        threadHelp.releaseLock()


def _getInstance(db):
    if db not in g_confdict:
        ilog.wflogger.warning("%s db does not exist." % (db))
        raise notExistMysqlInstance
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

    db_obj = MysqlTalker(host=host,
                         port=port,
                         db=db,
                         user=subdict["user"],
                         passwd=subdict["passwd"]
                         )
    return db_obj

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

# def getInstance(db):
#     if db not in g_confdict:
#         raise notExistMysqlInstance
#     subdict = g_confdict[db]
#     db_obj = MysqlTalker(host=subdict["host"],
#                             port=subdict["port"],
#                             db=subdict["db"],
#                             user=subdict["user"],
#                             passwd=subdict["passwd"]
#                             )
#     return db_obj


if "__main__" == __name__:
    import json
    pwd = os.path.dirname(os.path.realpath(__file__))
    mysql_conf = ("%s/../extractor/conf/mysql.conf") % (pwd)
    init(util.load_ini_conf(mysql_conf))
    instance = getInstance("spider")
    sql = "select id ,rootid, pattern_id, url, domainname, " \
          "urlmd5, cachever, type, refresh_cycle, opr_type, rank " \
          "from seed  " \
          "where status = 0"
    results = instance.query(sql)
    for result in results:
        print json.dumps(result)
        print "---------------------\n"

    one_result = instance.get(sql)
    print "urlmd5=%s" % (one_result["urlmd5"])
    print "---------------------\n"
    sql = "select * from query_playback where id = 434;"
    instance = getInstance("search")
    one_result = instance.get(sql)
    print "one_result query=%s" % (one_result["query"])
    print "---------------------\n"
    sql = "select * from query_playback where id in (434, 435);"
    results = instance.query(sql)
    for result in results:
        print "query=%s" % (result["query"])
    print "---------------------\n"

    sql = " create table test_by_test (" \
          "`id` int(11) unsigned," \
          "PRIMARY KEY (`id`)" \
          ")"
    instance.execute(sql)
    instance = getInstance("notexist")





    
