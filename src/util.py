#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os
import requests
import hashlib
import subprocess
import time
PWD = os.path.dirname(os.path.realpath(__file__))

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
            with open('net.err.log', 'a') as fh:
                fh.write("%s:ConnectionError\n" % (url))
            idx += 1
            time.sleep(5)
        except requests.exceptions.Timeout:
            with open('net.err.log', 'a') as fh:
                fh.write("%s:timeout\n" % (url))
            idx += 1
            time.sleep(5)
        except Exception as e:
            raise(e)
        raise('%s:out of max try times' %(url))


def jsDownloader(url, cookie_file):
    # js_file = "%s/phantom.js" % PWD
    js_file = "%s/casper.js" % PWD
    # cmd = '/usr/local/bin/phantomjs --load-images=false --ignore-ssl-errors=true --cookies-file=%s %s "%s" ' % (cookie_file, js_file, url)
    # cmd = '/usr/local/bin/phantomjs --load-images=false --ignore-ssl-errors=true  %s "%s" ' % (js_file, url)
    # cmd = '/Users/baidu/banmen/1688/_3rd_bin/casperjs/bin/casperjs %s --cookies-file=%s  --url="%s" ' % (js_file, cookie_file, url)
    cmd = '/Users/baidu/banmen/1688/_3rd_bin/casperjs/bin/casperjs %s --url="%s" ' % (js_file, url)
    print cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = p.stdout.readlines()
    # print res
    if res:
        return ''.join(res)
    else:
        return ''


def md5(data):
    m = hashlib.md5()
    try:
        m.update(data)
        return m.hexdigest()
    except Exception as e:
        m.update(data.encode("utf-8"))
        return m.hexdigest()

if __name__ == '__main__':
    content = jsDownloader('https://s.1688.com/selloffer/-C1ACD2C2C8B9-1045032.html?spm=b26110380.sw1688.0.0.nmZJ8S&earseFeat=true&cps=1&filterP4pIds=540123646135%2C537875729174%2C529751509712%2C533657062693%2C538898134101%2C528711569531%2C536143788646%2C538177573372&n=y&feature=32252%3B292980&pageOffset=0&uniqfield=pic_tag_id',
                       '/Users/baidu/banmen/1688/src/my_cookie.txt'
                       )

    if content:
        print 'success'
        open('content.html', 'w').write(content)
    else:
        print 'fail'
