# -*- coding: utf-8 -*-
import time
import re
import requests
from lxml import etree
import base64

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
    print len(topic)
    #这边返回36，与我实际的一样，所以话题是应该抓取成功了ww.zhihu.com/followed_topics?offset=0&limit=80'

def getxsrf():
    z = s.get('https://www.zhihu.com/topic#胸部',headers=HEADERS)
    _xsrf = etree.HTML(z.content).xpath('//input[@name="_xsrf"]/@value')[0]
    return _xsrf

def getimgsrc():
    # 获取xsrf
    _xsrf = getxsrf()
    # 把_xsrf添加到浏览器头
    HEADERS['X-Xsrftoken'] = _xsrf
    data = {'method': 'next',
            'params': '{"offset":1486212157.0,"topic_id":11385,"feed_type":"timeline_feed"}'}
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
            """
            生成图片名字 
            images -->['https://pic3.zhimg.com/v2-ce8a845a830a195f20538ea765b7fe9a_b.jpg']
            imagenames -->['v2-ce8a845a830a195f20538ea765b7fe9a_b.jpg']
            """
            imagebase64 = [base64_imgage(image) for image in images]
            answer_id = ll.xpath('//meta[@itemprop="answer-id"]/@content')[i]
            title = ll.xpath('//div[@class="feed-content"]/h2/a/text()')[i].strip()
            href = ll.xpath('//div[@class="zm-item-rich-text expandable js-collapse-body"]/@data-entry-url')[i]
            #时间戳
            data_score = ll.xpath('//div[@class="feed-item feed-item-hook  folding"]/@data-score')[i]
            print answer_id,title,href,data_score
#把图片转成 base64 
def base64_imgage(image):
    ir = s.get(url,headers=HEADERS)
    if ir.status_code == 200:
        return base64.b64encode(ir.content)
class checkyanzhi():
    def __init__(self,imagebase64):
        self.ss = requests.session()
        self.uploadurl = 'https://kan.msxiaobing.com/Api/Image/UploadBase64'
        self.yanzhiurl = 'https://kan.msxiaobing.com/ImageGame/Portal?task=yanzhi'
        self.processurl = 'https://kan.msxiaobing.com/Api/ImageAnalyze/Process'
        self.imagebase64 = imagebase64
    def upload(self):
        z = ss.post(self.uploadurl,self.imagebase64)
        ret = z.json()
        """
        返回值
        {u'Host': u'https://mediaplatform.msxiaobing.com',
            u'Url': u'/image/fetchimage?key=JMGqEUAgbwDVieSjh8AgKUq4khZmjMOAaWgzt4SRHupVmtMhpXE1ZRFbaX8'}
        """
        return '%s%s'%(ret['Host'],ret['Url'])
    
    def process(self):
        z1 = self.ss.get(self.yanzhiurl)
        #获取tid
        tid = etree.HTML(z1.content).xpath('//input[@name="tid"]/@value')[0]
        tm = time.time()
        data = {'MsgId':'%s' %int(tm*1000),'CreateTime':'%s' %int(tm),
                'Content[imageUrl]':self.upload()}
        z2 = self.ss.post(url=self.processurl,params={"service":"yanzhi",
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
        ret = z2.json()['content']['text']
        mark = re.findall(r"\d+\.?\d?",ret)
        print mark
if __name__ == '__main__':
    s = requests.session()
    getimgsrc()


