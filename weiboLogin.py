# -*- coding: utf-8 -*-

import requests
import rsa
import binascii
from urllib import quote
import base64
import time


class Weibo():
    def __init__(self):
        self.s = requests.Session()
        self.s.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'}

    def getsp(self, password, servertime, nonce, pubkey):
        u"使用rsa来加密password"
        rsapubkey = int(pubkey, 16)
        key = rsa.PublicKey(rsapubkey, 10001)
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
        passwd = rsa.encrypt(message, key)
        passwd = binascii.b2a_hex(passwd)
        return passwd

    def getsu(self, username):
        u'获取账号的base64'
        username = quote(username)
        return base64.encodestring(username).strip()

    def prologin(self, username):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            # 'callback':'sinaSSOController.preloginCallBack',
            'su': self.getsu(username),
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.15)',
            '_': int(time.time() * 1000)
        }
        z = self.s.get(url, params=params)
        return z.json()

    def login(self, username, password):
        '登录'
        url = 'http://login.sina.com.cn/sso/login.php'
        prolg = self.prologin(username)
        params = {'client': 'ssologin.js(v1.4.15)'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
                   'Referer': 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)',
                   }
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': '',
            'vsnf': '1',
            'su': self.getsu(username),
            'service': 'miniblog',
            'servertime': str(prolg['servertime']),
            'nonce': prolg['nonce'],
            'pwencode': 'rsa2',
            'rsakv': prolg['rsakv'],
            'sp': self.getsp(password=password, servertime=prolg['servertime'],
                             nonce=prolg['nonce'], pubkey=prolg['pubkey']),
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': '41',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        print data
        z = self.s.post(url, params=params, data=data, headers=headers)
        print z.content


if __name__ == '__main__':
    weibo = Weibo()
    weibo.login('13173740663', 'sssssssssss')
    # print weibo.getsp('aaaaaa','1493134039','Z5PBGE','EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443')

