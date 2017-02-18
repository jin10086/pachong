# -*- coding: utf-8 -*-
import time

import requests
from lxml import etree

S = requests.Session()
# 添加浏览器头
S.headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
def needCaptcha(username):
    url = 'http://cer.imufe.edu.cn/authserver/needCaptcha.html'
    params ={
        'username':username,
        '_':str(int(time.time()*1000))
    }
    '''
    username:152050119
    _:1487387939701
    '''
    z = S.get(url,params=params)
    print z.content
    if z.content.strip() == 'false':
        return True
    else:
        print u'需要验证码····'
        return False

def login(username,password):
    url = 'http://cer.imufe.edu.cn/authserver/login'
    z = S.get(url)
    ll = etree.HTML(z.content)
    lt = ll.xpath('//input[@name="lt"]/@value')[0]
    execution = ll.xpath('//input[@name="execution"]/@value')[0]
    _eventId = ll.xpath('//input[@name="_eventId"]/@value')[0]
    data = {'username':username,
            'password':password,
            'lt':lt,'execution':execution,
            '_eventId':_eventId,'signIn':''
    }
    postlogin = S.post(url,data=data)

if __name__ == '__main__':
    username = ''
    password = ''
    if needCaptcha(username):
        login(username,password)
        x = S.get('http://my.imufe.edu.cn/index.portal')
        ll = etree.HTML(x.content)
        print ll.xpath('//li[@id="welcomeMsg"]/text()')[0]
