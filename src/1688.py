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
from lxml import etree


def my_parse_qs(query):
    return dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])


def requests_ex(url, data=None, headers=None, params=None, cookies=None, proxies=None, timeout=100,
                    verify=False, retry_times=3):


    """ Requests封装避免抛未知异常, 且支持超时重试
        Args:
            data: string, If None, get; then post
            headers: dict, 请求头部, 默认None
            cookies: dict, 请求cookies, 默认None
            proxies: dict, 请求使用代理, 默认None
            timeout: int, 持续未接收到数据的最大时间间隔. 默认100
            verify: bool, 请求认证, 默认False
            retry_times: int. 超时重试次数, 默认3
    """

    idx = 0
    while idx < retry_times:
        try:
            if data is not None:
                res = requests.post(url=url, data=data, headers=headers, params=params, timeout=timeout,
                                    proxies=proxies, verify=verify, cookies=cookies)
            else:
                res = requests.get(url=url, headers=headers, params=params, timeout=timeout, proxies=proxies,
                                   verify=verify, cookies=cookies)
            return res
        except requests.exceptions.ConnectionError:
            with open('link.err.log', 'a') as fh:
                fh.write("%s:ConnectionError\n" % (url))
            idx += 1
        except requests.exceptions.Timeout:
            with open('link.err.log', 'a') as fh:
                fh.write("%s:timeout\n" % (url))
            idx += 1
        except Exception as e:
            raise(e)
        raise('out of max try times')

def process_url(url):
    try:
        process_url_raw(url)
    except Exception as e:
        with open('link.err.log', 'a') as fh:
            fh.write("%s\n" %(traceback.format_exc()))

def process_url_raw(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'referer': 'https://s.1688.com/selloffer/-C1ACD2C2C8B9-1031910.html?spm=a260k.635.1998214977.7.VIm1DN&cps=1&n=y&uniqfield=pic_tag_id',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }

    with open('link.url.txt', 'a') as fh:
        fh.write("%s\n" % (url))

    r = requests_ex(url, headers=headers)
    content = r.content.strip("\n,)")
    content_list = content.split('(')[1:]
    content = '('.join(content_list)
    content = content.replace("\\'", "'")
    res_json = json.loads(content.decode('gbk'))
    html_content = res_json['content']['offerResult']['html']
    root_node = etree.HTML(html_content)
    nodes = root_node.xpath('//a[@t-click-item="title"]')
    p = re.compile('(http|https)://detail\.1688\.com/offer/\d+.html')
    with open('link.txt', 'a') as fh:
        try:
            for node in nodes:
                href = node.attrib.get('href', "")
                if not href:
                    continue
                if not p.search(href):
                    continue
                fh.write(href + '\n')
        except Exception as e:
            pass
    time.sleep(1.5)

first_ajax_url = 'https://s.1688.com/selloffer/rpc_async_render.jsonp?cps=1&earseDirect=false&button_click=top&n=y&feature=12700%3B12078%3B74553&uniqfield=pic_tag_id&keywords=%C3%D4%B2%CA%B7%FE&categoryId=1048087&templateConfigName=marketOfferresult&offset=8&pageSize=60&asyncCount=20&startIndex=20&async=true&enableAsync=true&rpcflag=new&_pageName_=market&callback=jQuery1830299739098569038_1478156509635&_=1478156541902'
first_ajax_rec_url = 'https://s.1688.com/selloffer/rpc_async_render.jsonp?cps=1&earseDirect=false&button_click=top&n=y&feature=12700%3B12078%3B74553&uniqfield=pic_tag_id&keywords=%C3%D4%B2%CA%B7%FE&categoryId=1048087&templateConfigName=marketIndividuationAsync&offset=0&pageSize=5&asyncCount=5&startIndex=0&async=true&enableAsync=true&rpcflag=new&_pageName_=market&individualTypes=cfs_guess_user_prefer&categoryId=1048087&callback=jQuery1830299739098569038_1478156509635&excludeOfferIds=40368977892%2C534031422210%2C536371867536%2C536295441934%2C538254172140%2C529018483415%2C524131283200%2C43199921924%2C536861922047%2C527124597361%2C521130871045%2C259938363%2C538431442429%2C44109406020%2C532203553840%2C1043611328%2C539322932867%2C520649730471%2C526290038333%2C524259233670%2C1196311328%2C520509418550%2C536481267988%2C537208595954%2C538198936734%2C40982588499%2C536445783896%2C527147544951%2C37979701807%2C536393326429%2C520891706711%2C520556220937%2C523158234352%2C1254043347%2C536378884184%2C531920367287%2C523083635904%2C45429443863%2C38800730881%2C538679290480%2C44417308174%2C521768452383%2C43551636225%2C540611604461%2C40237197829%2C45220824542%2C532702180861%2C41895790966%2C523973173013%2C524808094141%2C37758769647%2C532149252128%2C521059282467%2C540490740070%2C538218561308%2C38515761286%2C40122167319%2C538131803922%2C537676903752%2C43265400117&_=1478156543196'
leftP4PIds = '536295441934,538254172140,529018483415,524131283200,43199921924,536861922047,527124597361,521130871045'

url_prefix, qs = first_ajax_url.split('?')
qs_dict = my_parse_qs(qs)

rec_url_prefix, rec_qs = first_ajax_rec_url.split('?')
rec_qs_dict = my_parse_qs(rec_qs)

# 第一页请求：
url = first_ajax_url
process_url(url)

qs_dict['startIndex'] = 40
qs_dict['_'] = int(time.time() * 1000)
url = url_prefix + '?' + urllib.urlencode(qs_dict)
# print url
process_url(url)

rec_qs_dict['_'] = int(time.time() * 1000)
rec_url = rec_url_prefix + '?' + urllib.urlencode(rec_qs_dict)
# print rec_url
process_url(rec_url)

#第2页之后的请求
total_page_num = 12
for page in xrange(2, total_page_num + 1):
    with open('link.log', 'a') as fh:
        fh.write('trace in page:%s\n' %(page))
    for sub_req in xrange(1, 4):
        qs_dict['startIndex'] = (sub_req - 1) * 20
        qs_dict['qrwRedirectEnabled'] = 'false'
        qs_dict['leftP4PIds'] = leftP4PIds
        qs_dict['filterP4pIds'] = leftP4PIds
        qs_dict['beginPage'] = page
        qs_dict['_'] = int(time.time() * 1000)
        if 1 == sub_req:
            if 'pageOffset' in qs_dict:
                del qs_dict['pageOffset']
                del qs_dict['leftP4PIds']
                del qs_dict['filterP4pIds']
                url = url_prefix + '?' + urllib.urlencode(qs_dict)
                url = '%s&leftP4PIds=%s&filterP4pIds=%s' % (url, leftP4PIds, leftP4PIds)
        else:
            qs_dict['pageOffset'] = (page -1) * 3
            url = url_prefix + '?' + urllib.urlencode(qs_dict)
        # print url
        process_url(url)

    rec_qs_dict['_'] = int(time.time() * 1000)
    rec_url = rec_url_prefix + '?' + urllib.urlencode(rec_qs_dict)
    # print rec_url
    process_url(rec_url)





