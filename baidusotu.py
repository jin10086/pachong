# -*- coding: utf-8 -*-

from __future__ import print_function

import time
import re
import json

import requests
from scrapy.selector import Selector
from fake_useragent import UserAgent
from textrank4zh import TextRank4Sentence

#获取N多的浏览器头
UA = UserAgent()
Headers = {'User-Agent':''}

#根据传入的图片地址，生成“标题”
def situ(imgurl):
    url = 'http://image.baidu.com/n/pc_search'
    params = {
        'rn':'10',
        'appid':'4',
        'tag':'1',
        'isMobile':'0',
        'queryImageUrl':imgurl,
        'querySign':'',
        'fromProduct':'',
        'productBackUrl':'',
        'fm':'chrome',
        'uptype':'plug_in'
    }
    Headers['User-Agent'] = UA.chrome
    z = requests.get(url,params=params,headers=Headers)
    response = Selector(text=z.content)
    # 关键词描述
    kw = response.css('.guess-info-word-highlight::text').extract_first()
    #百度百科名字
    bk = response.css('.guess-newbaike-name::text').extract_first()
    # 图片来源标题
    img_title = response.css('.source-card-topic-title-link::text').extract()
    #图片来源描述
    img_content = response.css('.source-card-topic-content::text').extract()
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=''.join(img_title), lower=True, source = 'all_filters')
    for item in tr4s.get_key_sentences(num=3):
        print(item.index, item.weight, item.sentence)

#获取百度下拉框
def baiduxiala(word):
    url = 'https://m.baidu.com/su'
    params = {
        'p':'3',
        'ie':'utf-8',
        'from':'wise_web',
        'wd':u'刘亦菲',
        't':str(int(time.time()*1000))
    }
    headers = {
        'Host':'m.baidu.com',
        'Referer':'https://www.baidu.com/',
        'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19'
    }
    z = requests.get(url,params=params,headers=headers,verify=False)
    words = re.findall('window.baidu.sug\((.*?)\);',z.content,re.U)
    if words:
        pass
    # print(z.json())

if __name__ == '__main__':
    baiduxiala(u'刘亦菲')
