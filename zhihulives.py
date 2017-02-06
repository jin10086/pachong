# coding: utf-8
# import time
import os
import requests
# import unicodecsv
basedir = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(os.path.join(basedir,'mysite'))
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django
django.setup()

from pachong.models import lives

headers = {
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding':'gzip, deflate, sdch, br',
    'accept-language':'zh-CN,zh;q=0.8',
    'cache-control':'max-age=0',
    'upgrade-insecure-requests':'1',
    'user-agent':'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    'Cookie':''
}
# def savetocsv(items):
#     with open('%s_lives.csv' %(time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())),'wb') as csvfile:
#         fieldnames = items[0].keys()
#         writer = unicodecsv.DictWriter(csvfile,fieldnames=fieldnames)
#         writer.writeheader()
#         for i in items:
#             try:
#                 writer.writerow(i)
#             except:
#                 pass

if __name__ == '__main__':
    # 分类
    url = 'https://api.zhihu.com/lives/special_lists?limit=100&offset=0&subtype=special_list'
    s = requests.session()
    s.headers = headers
    z = s.get(url).json()
    lives_ = z['data']
    for live in lives_:
        id = live['id']
        id_url = 'https://api.zhihu.com/lives/special_lists/%s/lives?limit=100&offset=10' %id
        z1 = s.get(id_url).json()['data']
        for _ in z1:
            #存储到数据库
            b = lives(live=_, id=_['id'], subject=_['subject'])
            b.save()
    is_end = z['paging']['is_end']
    # 如果还有下一页的话
    while not is_end:
        nexturl = z['paging']['next']
        z = s.get(nexturl).json()
        lives_ = z['data']
        for live in lives_:
            id = live['id']
            id_url = 'https://api.zhihu.com/lives/special_lists/%s/lives?limit=100&offset=10' % id
            z1 = s.get(id_url).json()['data']
            for _ in z1:
                #存储到数据库
                b = lives(live=_, id=_['id'], subject=_['subject'])
                b.save()
        is_end = z['paging']['is_end']
        
        
    # lives页面
    url = 'https://api.zhihu.com/lives/ongoing?purchasable=0&limit=100&offset=0'
    s = requests.session()
    s.headers = headers
    z = s.get(url)
    if z.status_code == 200:
        lives_ = z.json()['data']
        is_end = z.json()['paging']['is_end']
        for live in lives_:
            #存储到数据库
            b = lives(live=live,id=live['id'],subject=live['subject'])
            b.save()
        while not is_end:
            nexturl = z.json()['paging']['next']
            _ = s.get(nexturl).json()
            is_end = _['paging']['is_end']
            lives_ = _['data']
            for live in lives_:
                #存储到数据库
                b = lives(live=live, id=live['id'], subject=live['subject'])
                b.save()