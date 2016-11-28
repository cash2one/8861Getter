#!/usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import json
import urlparse
import urllib
import traceback
import time
import re
import time
import os
import threading
from threading import current_thread
from lxml import etree
# import util
from common import ilog
from common import util
from common import mysqlTalker

class AKindCrawler(object):
    def __init__(self, url, feature_params, cookie_file, cate):
        self._url = url
        self._cate = cate
        self._feature_params = feature_params
        _tmp_dir = 'tmp/%s' % self._cate
        if not os.path.exists(_tmp_dir):
            os.makedirs(_tmp_dir)
        self._first_page_html_file = '%s/%s.html' % (_tmp_dir, self._feature_params)
        self._cookie_file = cookie_file
        # self._init_cookie_file(cookie_file)
        self._headers = self._get_heades()
        self._total_pages = 0
        self._total_item_cnt = 0
        self._first_ajax_url = ''
        self._leftP4PIds = ''
        self._page_size = 60
        self._ajax_size = 20
        self._max_page_cnt = 100
        self._url_filter = re.compile('(http|https)://detail\.1688\.com/offer/\d+.html')
        self._ajax_url_prefix = ''
        self._ajax_qs_dict = {}


    def _init_cookie_file(self, cookie_file):
        self._cookie_file = cookie_file + '.' + threading.current_thread().getName()
        open(self._cookie_file, "wb").write(open(cookie_file, "rb").read())

    def _my_parse_qs(self, query):
        return dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

    def _get_keywords(self, query):
        qs_list = query.split('&')
        for one_qs in qs_list:
            if -1 != one_qs.find('keywords='):
                self._keywords = one_qs.split('=')[1]
                return
            continue

    def _get_heades(self, hasreferer=True):
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            # 'referer': self._url,
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        if hasreferer:
            _headers['referer'] = self._url
        return _headers

    def _recode_detail_url(self, offerid, pic_url):
        url = 'https://detail.1688.com/offer/%s.html' % offerid
        with open('url.txt', 'a') as fh:
            fh.write('%s\t%s\n' % (url, pic_url))
        urlmd5 = util.md5(url)
        sql = 'select urlmd5 from resource where urlmd5="%s" ' % urlmd5
        result = mysqlTalker.getInstance("spider").get(sql)
        if result:
            ilog.logger.debug('%s has been extracted.' % url)
            return

        sql = 'insert into resource (url, urlmd5, pic_url, cate) values("%s", "%s", "%s", "%s")' \
              % (url, urlmd5, pic_url, self._cate)
        mysqlTalker.getInstance("spider").execute(sql)
        ilog.logger.debug('new-extracted:%s.' % url)

    def _load_first_page_html(self):
        # return util.jsDownloader(self._url, self._cookie_file)
        r = util.requests_ex(self._url, headers=self._get_heades(hasreferer=False))
        if not r:
            ilog.wflogger.warn('fail to down:%s' % self._url)
            return None
        return r.content

    def _process_ajax_req(self, url):
        try:
            time.sleep(12.5)
            with open('link.url.txt', 'a') as fh:
                fh.write("%s\n" % (url))

            r = util.requests_ex(url, headers=self._headers)
            with open('ajax.html', 'w') as fh:
                fh.write(r.content)
            content = r.content.strip("\n,)")
            content_list = content.split('(')[1:]
            content = '('.join(content_list)
            content = content.replace("\\'", "'")
            res_json = json.loads(content.decode('gbk'))
            html_content = res_json['content']['offerResult']['html']
            root_node = etree.HTML(html_content)
            # open('ajax.html', 'w').write(html_content)
            self._get_items_info(url, root_node)
        except Exception as e:
            ilog.wflogger.warn('AKindCrawler::_process_ajax_req fail.url=%s, error=%s' % (url, traceback.format_exc()))



    def _get_items_info(self, url, root_node):
        # nodes = root_node.xpath('//a[@offerid]')
        nodes = root_node.xpath('//div[@class="imgofferresult-mainBlock"]')
        # p = re.compile('(http|https)://detail\.1688\.com/offer/\d+.html')
        try:
            for node in nodes:
                offerid_node = node.xpath('.//a[@offerid]')
                if not offerid_node:
                    ilog.logger.debug('%s has none offerid node.' % url)
                    continue
                offerid_node = offerid_node[0]
                offerid = offerid_node.attrib.get('offerid', "")
                if not offerid:
                    ilog.logger.debug('%s has a offerid node with no offerid attr.' % url)
                    continue
                pic_url_node = node.xpath('.//img')
                if not pic_url_node:
                    ilog.logger.debug('%s has none img node.' % url)
                    continue
                pic_url_node = pic_url_node[0]
                pic_url = pic_url_node.attrib.get('src', "")
                if not pic_url:
                    pic_url = pic_url_node.attrib.get('data-lazy-src', "")
                    if not pic_url:
                        ilog.logger.debug('%s has a offerid node with no src or data-lazy-src attr.' % url)
                        continue
                self._recode_detail_url(offerid, pic_url)
        except Exception as e:
            ilog.wflogger.warn('AKindCrawler::_getItemInfos fail.url=%s, error=%s' % (url, traceback.format_exc()))


    def _process_first_page_ajax(self):
        # 第一页第一个ajax请求
        self._process_ajax_req(self._first_ajax_url)

        # 第一页第二个ajax请求
        self._ajax_qs_dict['_'] = int(time.time() * 1000)
        _ajax_url = self._url_prefix + '?' + urllib.urlencode(self._ajax_qs_dict)
        self._process_ajax_req(_ajax_url)

    def _process_other_pages_ajax(self):
        for page in xrange(2, self._total_pages + 1):
            ilog.logger.debug('process sub_cate:%s, page:%s' % (self._url, page))
            for sub_req in xrange(1, 4):
                self._ajax_qs_dict['startIndex'] = (sub_req - 1) * 20
                self._ajax_qs_dict['qrwRedirectEnabled'] = 'false'
                self._ajax_qs_dict['leftP4PIds'] = self._leftP4PIds
                self._ajax_qs_dict['filterP4pIds'] = self._leftP4PIds
                self._ajax_qs_dict['beginPage'] = page
                self._ajax_qs_dict['_'] = int(time.time() * 1000)
                if 1 == sub_req:
                    if 'pageOffset' in self._ajax_qs_dict:
                        del self._ajax_qs_dict['pageOffset']
                        del self._ajax_qs_dict['leftP4PIds']
                        del self._ajax_qs_dict['filterP4pIds']
                    url = self._url_prefix + '?' + urllib.urlencode(self._ajax_qs_dict)
                    url = '%s&leftP4PIds=%s&filterP4pIds=%s' % (url, self._leftP4PIds, self._leftP4PIds)
                    url += '&keywords=%s' % self._keywords
                else:
                    self._ajax_qs_dict['pageOffset'] = (page - 1) * 3
                    url = self._url_prefix + '?' + urllib.urlencode(self._ajax_qs_dict)
                    url += '&keywords=%s' % self._keywords
                # print url
                self._process_ajax_req(url)

    def _process_first_page(self):
        _html_content = self._load_first_page_html()
        if not _html_content:
            # 前面已经记录错误信息，此处没必要记录
            return
        with open(self._first_page_html_file, 'w') as fh:
            fh.write(_html_content)
        if not _html_content:
            return
        # _html_content = _html_content.decode('gbk')
        root_node = etree.HTML(_html_content)
        item_cnt_nodes = root_node.xpath('//div[@class="sm-side"]/span[@class="sm-widget-offer"]/em')
        if not item_cnt_nodes:
            ilog.wflogger.warn('no product item:%s' % self._url)
            return
        _total_item_cnt = int(item_cnt_nodes[0].text)
        print '_total_item_cnt:%s' % _total_item_cnt
        self._total_item_cnt = _total_item_cnt

        # 先保存首页的商品信息
        self._get_items_info(self._url, root_node)

        if 0 == self._ajax_size:
            self._print_info()
            return

        if _total_item_cnt < self._ajax_size:
            self._print_info()
            return

        # itemNOdes = root_node.xpath('//div[@class="sm-offer "]//li[@t-rank]')
        # for node in itemNOdes:
        #     offerid = node.attrib.get('t-offer-id', "")
        #     print offerid
        #
        #
        #     self._recode_detail_url



        _page_cnt = int(_total_item_cnt / self._page_size) + 1
        if _page_cnt < 2:
            self._total_pages = _page_cnt
        else:
            _page_cnt = int (_page_cnt * 1.3)
            self._total_pages = min(self._max_page_cnt, _page_cnt)

        _first_ajax_nodes = root_node.xpath('//div[@id="sm-maindata"]//div[@data-mod-config]')
        _first_ajax_str = _first_ajax_nodes[0].get('data-mod-config', "")
        _first_ajax_url = json.loads(_first_ajax_str)['url']
        # print '_first_ajax_url:%s' % _first_ajax_url
        self._url_prefix, qs = _first_ajax_url.split('?')
        self._ajax_qs_dict = self._my_parse_qs(qs)
        self._ajax_qs_dict['callback'] = 'jQuery18309910704592438462_%s' % str(int(time.time() * 1000) - 15432)
        self._ajax_qs_dict['_'] = int(time.time() * 1000)
        # self._keywords = self._ajax_qs_dict['keywords']
        del self._ajax_qs_dict['keywords']
        self._get_keywords(qs)
        self._first_ajax_url = self._url_prefix + '?' + urllib.urlencode(self._ajax_qs_dict)
        self._first_ajax_url += '&keywords=%s' % self._keywords
        
        p4pIdsNodes = root_node.xpath('//ul[@id="sm-offer-list"]')
        p4pIds_str = p4pIdsNodes[0].get('data-p4p-info', '')
        self._leftP4PIds = json.loads(p4pIds_str)['p4pIds']

        self._print_info()

        if '' != self._first_ajax_url and '' != self._leftP4PIds:
            self._process_first_page_ajax()

    def _print_info(self):
        msg = '\n-----------------------------------------\n'
        msg += '_cate:%s\n' % (self._cate)
        msg += '_url:%s\n' % self._url
        msg += '_first_ajax_url:%s\n' % self._first_ajax_url
        msg += '_leftP4PIds:%s\n' % self._leftP4PIds
        msg += '_total_item_cnt:%s\n' % self._total_item_cnt
        msg += '_total_pages:%s\n' % self._total_pages
        msg += '-----------------------------------------'
        ilog.logger.debug(msg)
        if self._total_item_cnt > 6000:
            ilog.wflogger.warn(msg)

    def work(self):
        try:
            if os.path.exists(self._first_page_html_file):
                ilog.logger.debug('[%s][%s] %s has processed.' % (self._cate, self._feature_params, self._url))
                return
            self._process_first_page()
            if self._total_pages < 2:
                return
            if '' != self._first_ajax_url and '' != self._leftP4PIds:
                self._process_other_pages_ajax()
        except Exception as e:
            ilog.wflogger.warn('AKindCrawler::work fail.error:%s' % traceback.format_exc())

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    url = 'https://s.1688.com/selloffer/-C1ACD2C2C8B9-1045032.html?spm=b26110380.sw1688.0.0.sGI3Cd&earseFeat=true&filterP4pIds=540123646135%2C537875729174%2C529751509712%2C533657062693%2C538898134101%2C528711569531%2C536143788646%2C538177573372&cps=1&n=y&feature=32252&pageOffset=0&uniqfield=pic_tag_id'
    crawler = AKindCrawler(url, '/Users/baidu/banmen/1688/src/my_cookie.txt')
    crawler.work()
        
        
        




