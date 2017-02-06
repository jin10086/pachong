# coding: utf-8
# import time
import requests
# import unicodecsv
import sys
sys.path.append(r'D:\GITHUB\ttt\mysite')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django
django.setup()

from dl.models import lives

headers = {
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding':'gzip, deflate, sdch, br',
    'accept-language':'zh-CN,zh;q=0.8',
    'cache-control':'max-age=0',
    'upgrade-insecure-requests':'1',
    'user-agent':'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    'Cookie':'udid="AEDAburZlgmPTmHv2f9hmE3K6IsuCjeWUMs=|1457522277"; d_c0="ACDAcxWWpAmPTjIflnNlxJB0Yn-OjK10VpQ=|1458444019"; _zap=a2956bc3-ea8b-48c6-af3b-8bcd57ecd6e1; q_c1=e152ba40b15a4a8484ff75eebc228c1f|1484275515000|1472553889000; l_cap_id="Y2E1Mjk3YTUzMzE5NDk5ZWFhZDJjZTk1NWFmMjlhZmY=|1484275515|e17a97e344a89b9408b8f9f499620434128bb781"; cap_id="MTM4NWVmZGM5MjY1NDkyNjlmZGFlNDFjZWUwYjkwZGY=|1484275515|1680e0729962bddafbb38ec24a45c83f873c32ed"; r_cap_id="OWRlZGE3NWQwZWFlNGM2MjhmMjU2ZTIyZmRhZWU4MzI=|1484275518|25216d2365246e0ad54953c767acd879b7ae2608"; login="NDRiNmVjZDM5NjIzNGZlN2FiNDFlYTMxNjQ1NzAxZWQ=|1484275542|68e85244a3220f43b689384e03d08b490467cf67"; aliyungf_tc=AQAAAP9g4gkGMgYA/71BcDYhTD+XOrfF; z_c0=Mi4wQUJCS0ktVFhkZ2tBSU1CekZaYWtDUmNBQUFCaEFsVk5Wc3lmV0FCZHp3MHVxeEhzdU4tYzdTVTJyNTB4T291UXBn|1485492340|014c30799ffaa3adde0ca57697baf5a728574d0b; __utma=155987696.842079663.1485492110.1485492110.1485492110.1; __utmb=155987696.0.10.1485492110; __utmc=155987696; __utmz=155987696.1485492110.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
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
            b = lives(live=live,id=live['id'],subject=live['subject'])
            b.save()
        while not is_end:
            nexturl = z.json()['paging']['next']
            _ = s.get(nexturl).json()
            is_end = _['paging']['is_end']
            lives_ = _['data']
            for live in lives_:
                b = lives(live=live, id=live['id'], subject=live['subject'])
                b.save()