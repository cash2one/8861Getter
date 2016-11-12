#!/usr/bin/env python
#coding=utf-8

#资源若存在，是否强制更新
UPDATE_FORCE_TRUE = "0"
UPDATE_FORCE_FALSE = "1"

#资源爬取状态
CRAWLED = 0
COLLECTD_NOT_CRAWLED = 1
NOT_COLLECTED = 2

#最大最小更新周期
DEFAULT_MIN_REFRESH_CYCLE = 5
DEFAULT_MAX_REFRESH_CYCLE = 30 * 24 * 3600
#默认更新周期
DEFAULT_REFRESH_TIME = 24 * 3600 #1 day
#不可到达更新周期
NEVER_REFRESH_CYCLE = 70 * 365 * 24 * 3600 #70 years

#不可到达时间
NEVER_UPTO_TIME = "2099-12-29 23:59:59"

#是否是自更新,0为是 1为不是
SELF_UPDATE_TRUE = 0
SELF_UPDATE_FALSE = 1

#是否固定资源爬取更新周期
#固定
FIX_REFRESH_TIME_TRUE = "0"
#不固定
FIX_REFRESH_TIME_FALSE = "1"

#是否需要js加载
#不需要
NO_JS_ACTION_ID = "-1"
#页面初始化加载
LOAD_JS_ACTION_ID = "0"

#是否需要本定保存资源
NEED_STORE_TRUE = "0"
NEED_STORE_FALSE = "1"

FOLLOW_FATHER_PATTERN_ID = "-1"

FOLLOW_FATHER_HTTP_PARAMS_ID = "-1"

FOLLOW_FATHER_TRAFFIC_ID = "-1"

#是否关闭内存cache
NO_MEM_CACHE = False

#是否强制更新内存cache
REFRESH_MEM_CACHE_FORCE_TRUE = 0
REFRESH_MEM_CACHE_FORCE_FALSE = 1

#js action 类型
IS_COMMON_JS_ACTION = 0 #普通点击或普通滚动
IS_INFINITE_SCROLL = 1 #无限滚动加载内容到当前页面
IS_INFINITE_CLICK = 2 #滚动到页底,然后点击按钮加载最新内容到当前页面

# 是否放开分表模式
SPLIT_TBL_MODE = 0
NO_SPLIT_TBL_MODE = 1

SELECTOR_SVR = 'http://127.0.0.1:8866/selector/internal'
SELECTOR_PATTERN = '%s?tgt=pattern' % (SELECTOR_SVR)
SELECTOR_JS_ACTION = '%s?tgt=js_action' % (SELECTOR_SVR)
SELECTOR_HTTP_PARAMS = '%s?tgt=http_params' % (SELECTOR_SVR)

CRAWER_API_URL = 'http://127.0.0.1:8866/crawler/api'

VALID_STATUS = 0
#js action 类型
IS_NO_JS_ACTION = -1
IS_COMMON_JS_ACTION = 0 #普通点击或普通滚动
IS_INFINITE_SCROLL = 1 #无限滚动加载内容到当前页面
IS_INFINITE_CLICK = 2 #滚动到页底,然后点击按钮加载最新内容到当前页

#project
DEFAULT_PROJECT = 'spider'
# PROJECT = DEFAULT_PROJECT

# def setProject(name="spider"):
#     global PROJECT
#     PROJECT = name
#
# def getProject():
#     return PROJECT

DEFAULT_MODULE_NAME = "extractor.src.wdParser"
PRO_MODULE_MAP = {
    'spider': DEFAULT_MODULE_NAME,
    'pcSpider': DEFAULT_MODULE_NAME,
    'mmVideoSpider': 'extractor.src.mmVideoWdParser',
    'hunterSpider': 'extractor.src.mmVideoWdParser'
}




