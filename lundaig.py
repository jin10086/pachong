# -*- coding: utf-8 -*-
from concurrent import futures
import time
import re
import random
import logging
import requests
from lxml import etree
import base64
import os
basedir = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(os.path.join(basedir,'mysite'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django
django.setup()

from pachong.models import zhihudaiguang

HEADERS = {
    'Cookie':'aliyungf_tc=AQAAAJoqcw1qvwIAa9KgtE4hNNwwiC+T; q_c1=fae863417aa447b7af04dcf2a704c01f|1486204080000|1486204080000; _xsrf=acea3e0cb2ccdc6ca9ff149776a0c1da; l_cap_id="MWYxNzIzMzUwNzZkNDEzMTkwN2UxMDY2M2U5YTU5Yzc=|1486204080|0fdccdb7ae2bab48441eb9903b7022355256c360"; cap_id="MzViMWVkNDc0MzFhNGU0ZTkyNWM3ZmRkY2VmNDFmZmY=|1486204080|26eba0c9408a73dd5804798c4fe944bf420bac93"; _zap=ab02de8b-5911-4842-b807-5c0555657f41; d_c0="ACDC1k8-QguPTtp_xvh0EpYybObAcbLgPUc=|1486204080"; login="MDhmOTBmMzVmNmExNDlkNjhhZjU3ZGVlZGNjZDVhNzM=|1486204093|58158eb04805198146c489d8a686d06131bd3552"; n_c=1; __utmt=1; __utma=51854390.1877980709.1486206322.1486206322.1486206322.1; __utmb=51854390.8.10.1486206322; __utmc=51854390; __utmz=51854390.1486206322.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100--|2=registration_date=20160916=1^3=entry_date=20160916=1; z_c0=Mi4wQUdDQU5lTHRqQW9BSU1MV1R6NUNDeGNBQUFCaEFsVk54am05V0FEaklzYVJKNkpKdmpuSTNzX0diai1XWmRMemt3|1486206483|be5a953a5929bb534e4178d898f7d1342e17efc6',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}

def getalltopic():
    # 获取话题的url，注意 offset已经改为了0，表示从0开始后面的80条
    url = 'https://www.zhihu.com/followed_topics?offset=0&limit=80'
    z = s.get(url,headers=HEADERS)
    #获取所有话题
    topic = z.json()['payload']
    #打印出关注了多少条话题
    # print len(topic)
    #这边返回36，与我实际的一样，所以话题是应该抓取成功了ww.zhihu.com/followed_topics?offset=0&limit=80'
    return [i['id'] for i in topic]

def getxsrf():
    z = s.get('https://www.zhihu.com/topic#胸部',headers=HEADERS)
    _xsrf = etree.HTML(z.content).xpath('//input[@name="_xsrf"]/@value')[0]
    return _xsrf

def getimgsrc(offset,topic_id):
    # 获取xsrf
    _xsrf = getxsrf()
    # 把_xsrf添加到浏览器头
    HEADERS['X-Xsrftoken'] = _xsrf
    data = {'method': 'next',
            'params': '{"offset":%s,"topic_id":%s,"feed_type":"timeline_feed"}' %(offset,topic_id)}
    z1 = s.post('https://www.zhihu.com/node/TopicFeedList',
                data=data, headers=HEADERS)
    #把所有的html代码拼接起来
    html = ''.join(z1.json()['msg'])
    ll = etree.HTML(html)
    #获取当前回答的所有内容
    contents = ll.xpath('//textarea[@class="content"]/text()')
    for i in range(len(contents)):
        #提取出其中的图片地址
        images = etree.HTML(contents[i]).xpath('//img/@src')
        #如果图片不为0的话，则得到answer-id，点赞会用到
        if len(images)!= 0:
            xiaobing = []
            fs = []
            is_sex = False
            try:
                #如果图片大于3张，则随机选3张
                if len(images) > 3:
                    images_ = random.sample(images,3)
                else:
                    images_ = images

                with futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_url = dict((executor.submit(process,base64_imgage(image)), image)
                                        for image in images_)

                    for future in futures.as_completed(future_to_url):
                        url = future_to_url[future]
                        if future.exception() is not None:
                            print('%r generated an exception: %s' % (url,
                                                                    future.exception()))
                        else:
                            xiaobing.append(future.result())
                # 获取分数
                fs = [re.search(r"\d+\.?\d?",xx['content']['text']).group() for xx in xiaobing if re.search(r"\d+\.?\d?",xx['content']['text'])]
                if len(fs) != 0:
                    if float(max(fs)) > 7.5:
                        is_sex = True
            except Exception as ex:
                logging.exception('yanzhi check error')
            answer_id = ll.xpath('//meta[@itemprop="answer-id"]/@content')[i]
            title = ll.xpath('//div[@class="feed-content"]/h2/a/text()')[i].strip()
            href = ll.xpath('//div[@class="zm-item-rich-text expandable js-collapse-body"]/@data-entry-url')[i]
            #时间戳
            data_score = ll.xpath('//div[@class="feed-item feed-item-hook  folding"]/@data-score')[i]
            #存储到数据库
            b = zhihudaiguang(imageurl=images,id=answer_id,title=title,href=href,content=contents,
                                        data_score=data_score,xiaobing=xiaobing,topic_id=topic_id,is_sex=is_sex,fs=fs)
            b.save()

#把图片转成 base64 
def base64_imgage(url):
    ir = s.get(url,headers=HEADERS)
    if ir.status_code == 200:
        return base64.b64encode(ir.content)
def vote_up(answer_id):
    url = 'https://www.zhihu.com/node/AnswerVoteBarV2'
    data = {'method':'vote_up',
            'params':'{"answer_id":"%s" % answer_id}'}
    # 获取xsrf
    _xsrf = getxsrf()
    # 把_xsrf添加到浏览器头
    HEADERS['X-Xsrftoken'] = _xsrf
    z2 = s.post(url,data=data,headers=HEADERS)
    if z2.status_code == 200:
        #如果msg不为空，表示点赞出错.
        if z2.json()['msg'] != None:
            print z2.json()['msg']
        

def upload(imagebase64):
    uploadurl = 'https://kan.msxiaobing.com/Api/Image/UploadBase64'
    z = ss.post(uploadurl,imagebase64)
    ret = z.json()
    """
    返回值
    {u'Host': u'https://mediaplatform.msxiaobing.com',
        u'Url': u'/image/fetchimage?key=JMGqEUAgbwDVieSjh8AgKUq4khZmjMOAaWgzt4SRHupVmtMhpXE1ZRFbaX8'}
    """
    return '%s%s'%(ret['Host'],ret['Url'])

def process(imagebase64):
    yanzhiurl = 'https://kan.msxiaobing.com/ImageGame/Portal?task=yanzhi'
    processurl = 'https://kan.msxiaobing.com/Api/ImageAnalyze/Process'
    z1 = ss.get(yanzhiurl)
    #获取tid
    tid = etree.HTML(z1.content).xpath('//input[@name="tid"]/@value')[0]
    tm = time.time()
    data = {'MsgId':'%s' %int(tm*1000),'CreateTime':'%s' %int(tm),
            'Content[imageUrl]':upload(imagebase64)}
    z2 = ss.post(url=processurl,params={"service":"yanzhi",
                    "tid":tid},data=data)
    """
    返回值 
        {
            "msgId": "1486513023436",
            "timestamp": 0,
            "receiverId": null,
            "content": {
                "text": "妹子竟有8.8分颜值，美得无法直视，多少直男竞折腰，腰，腰",
                "imageUrl": "http://mediaplatform.trafficmanager.cn/image/fetchimage?key=UQAfAC8ABAAAAFcAFgAGABYASgBGADgANQA4ADcANQBCAEQANwAzADQANwA0AEQAMAAzADAAQQBGADQAMgA3ADIAQwBFADYAMgAxAEUAMABFADIA",
                "metadata": {
                "AnswerFeed": "FaceBeautyRanking",
                "w": "vc_YiuTzgvP2h_PAW0tgjOnpoMH5vendgPXvgubnhNHehfL4j9L6rvjRsM7ngPXvgPzzhN_YhP7sjvXYrsj7vuP5h8zTiuTlier5jNnUgeTf",
                "aid": "AFC44578B499147016D1C68CDC73F993"
                            }
                        }
        }
    """
    return z2.json()
#获取最新的 话题时间
def getmaxtopic(topic_id):
    try:
        return zhihudaiguang.objects.filter(topic_id=topic_id).values_list('data_score',flat=True).order_by('-data_score')[0]
    except Exception as ex:
        logging.exception('get max time error')
        return None
if __name__ == '__main__':
    s = requests.session()
    ss = requests.session()
    ss.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                    'Accept-Language':'zh-CN,zh;q=0.8'}
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_topic = dict((executor.submit(getimgsrc,0,i), i)
                                        for i in getalltopic())
                    for future_ in futures.as_completed(future_to_topic):
                        url = future_to_topic[future_]
                        if future_.exception() is not None:
                            print('%r generated an exception: %s' % (url,
                                                                    future_.exception()))
    


