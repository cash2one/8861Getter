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
import copy
from lxml import etree
# import util
from common import ilog
from common import util

class SubCateBuilder(object):

    def __init__(self, seed, cate, cookie_file, filter_feature_index_list, enable_price_filter):
        self._seed = seed
        self._cookie_file =cookie_file
        self._filter_feature_index_list = filter_feature_index_list
        self._enable_price_filter = enable_price_filter
        self.sub_cate_url_list = []
        self._all_feature_info_list = []
        self._all_feature_code_list = []
        self._html_content = None
        self._total_item_cnt = 0
        self._cate = cate
        self._init()

    def _headers(self):
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            # 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            # 'Cookie': self._cookie
        }
        return _headers

    def _get_html_content(self, url):
        r = util.requests_ex(url, headers=self._headers())
        return r.content


    def _init(self):
        self.sub_cate_url_list.append(self._seed)
        self._html_content = self._get_html_content(self._seed)
        # self._html_content = util.jsDownloader(self._seed, self._cookie_file)
        with open('seed.html', 'w') as fh:
            fh.write(self._html_content)
        self._build()

    def _genFeatureParams(self, feature_list, result_list=[]):
        if not feature_list:
            return result_list
        sub_list = feature_list.pop(0)
        # print json.dumps(sub_list)
        if not result_list:
            for attr in sub_list:
                result_list.append(attr)
        else:
            tmp_result_list = []
            for attr in sub_list:
                for attr_res in result_list:
                    tmp_result_list.append('%s;%s' % (attr_res, attr))
            # print json.dumps(tmp_result_list)
            result_list = tmp_result_list
        if feature_list:
            return self._genFeatureParams(feature_list, result_list)
        else:
            return result_list

    def _build(self):
        root_node = etree.HTML(self._html_content)
        item_cnt_nodes = root_node.xpath('//div[@class="sm-side"]/span[@class="sm-widget-offer"]/em')
        if not item_cnt_nodes:
            return
        self._total_item_cnt = int(item_cnt_nodes[0].text)

        nodes = root_node.xpath('//div[@class="sm-widget-sngroup"]//div[@type="feature"]')
        feature_list = []
        i = 1
        for node in nodes:
            sub_feature_code_list = []
            sub_feature_name_code_list = []
            value_nodes = node.xpath('.//li//a[@data-value]')
            for value_node in value_nodes:
                name = value_node.attrib.get('title', "")
                value = value_node.attrib.get('data-value', "")
                sub_feature_name_code_list.append('%s_%s' % (name, value))
                sub_feature_code_list.append('%s' % value)
            self._all_feature_info_list.append(sub_feature_name_code_list)
            self._all_feature_code_list.append(sub_feature_code_list)

            if i in self._filter_feature_index_list:
                feature_list.append(sub_feature_code_list)
            i += 1

        price_nodes = root_node.xpath('//div[@class="sm-widget-sngroup"]//div[@type="feature_price"]')
        price_feature_list = []
        value_nodes = price_nodes[0].xpath('.//li/a')
        for value_node in value_nodes:
            name = value_node.attrib.get('cvalue', "")
            price_feature_list.append('%s' % name)

        tmp_list = copy.deepcopy(feature_list)
        feature_params_list = self._genFeatureParams(tmp_list)
        ilog.logger.debug( '+++++++++++++ total %s groups +++++++++++++++' % len(feature_params_list))
        qs_plus_dict = {}
        for feature_param in feature_params_list:
            qs_plus_dict['feature'] = feature_param
            if self._enable_price_filter:
                for price in price_feature_list:
                    # price_feature_list = ["p_0-50", "p_50-70", "p_70-110", "p_110-160", "p_160-500", "p_500-"]
                    p_list = price.split('_')[1].split('-')
                    qs_plus_dict['priceStart'] = p_list[0]
                    if len(p_list) > 1 and p_list[1]:
                        qs_plus_dict['priceEnd'] = p_list[1]
                    self.sub_cate_url_list.append('%s&%s' % (self._seed, urllib.urlencode(qs_plus_dict)))
                    if 'priceEnd' in qs_plus_dict:
                        del qs_plus_dict['priceEnd']
                    if 'priceStart' in qs_plus_dict:
                        del qs_plus_dict['priceStart']
            else:
                self.sub_cate_url_list.append('%s&%s' % (self._seed, urllib.urlencode(qs_plus_dict)))
                qs_plus_dict.clear()

    def print_feature_info(self, _to_screen=True):
        # print json.dumps(self._all_feature_info_list)
        i = 1
        msg = '\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n'
        msg += '%s: total_item_cnt=%s\n' % (self._cate, self._total_item_cnt)
        msg += '---------------------------------------------------------\n\n'
        tmp_dict1 = {}
        tmp_dict2 = {}
        for one_feature_list in self._all_feature_info_list:
            one_feature_code_list = self._all_feature_code_list[i-1]
            feature_codes = ','.join(one_feature_code_list)
            feature_str = '\t'.join(one_feature_list)
            feature_len = len(one_feature_list)
            item_cnt = self._get_subCate_itemCnt(feature_codes)
            # feature_msg = '[feature list %s : feature_list_len=%s, all_item_cnt=%s] [feature_codes: %s] %s\n' \
            #           % (i, feature_len, item_cnt, feature_codes, feature_str)
            feature_msg = '[feature list %s : feature_list_len=%s, all_item_cnt=%s]  %s\n' \
                         % (i, feature_len, item_cnt, feature_str)
            # print feature_msg
            tmp_dict1[i] = item_cnt
            tmp_dict2[i] = feature_msg
            time.sleep(10)
            i += 1
        sorted_list = sorted(tmp_dict1.iteritems(), key=lambda d: d[1], reverse=True)
        for item in sorted_list:
            msg += tmp_dict2[item[0]]
            msg += '-------------------------------------------------------------------\n\n'
        msg += '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n'
        if _to_screen:
            print msg
        else:
            ilog.logger.debug(msg)



    def _get_subCate_itemCnt(self, feature_codes):
        qs_plus_dict = {}
        qs_plus_dict['feature'] = feature_codes
        url = '%s&%s' % (self._seed, urllib.urlencode(qs_plus_dict))
        cnt = 0
        try:
            html_content = self._get_html_content(url)
            root_node = etree.HTML(html_content)
            item_cnt_nodes = root_node.xpath('//div[@class="sm-side"]/span[@class="sm-widget-offer"]/em')
            if not item_cnt_nodes:
                cnt = 0
            cnt = int(item_cnt_nodes[0].text)
            ilog.logger.debug('SubCateBuilder::_get_subCate_itemCnt. %s: %s finds %s items.' % (self._cate, url, str(cnt)))
        except Exception as e:
            ilog.wflogger.warn('SubCateBuilder::_get_subCate_itemCnt failed. url=%s, error=%s' % (url, traceback.format_exc()))
        return cnt

    def print_sub_url_info(self):
        for url in self.sub_cate_url_list:
            print '%s' % url
        print '+++++++++++++ total %s urls +++++++++++++++' % len(self.sub_cate_url_list)

    def get_sub_url_info(self):
        return self.sub_cate_url_list


