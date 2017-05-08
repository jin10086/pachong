# coding: utf-8

import cPickle as pickle
import requests
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
from pymongo import MongoClient
client = MongoClient()
db = client.loc
collection = db.mobai1

def load_url(url, params, timeout, headers=None):
    return requests.get(url, params=params, timeout=timeout, headers=headers).json()


def getloc():
    allloc = []
    u"""利用高德地图api获取上海所有的小区坐标
    http://lbs.amap.com/api/webservice/guide/api/search/#text
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        url = 'http://restapi.amap.com/v3/place/text'
        param = {
            'key': '22d6f93f929728c10ed86258653ae14a',
            'keywords': u'小区',
            'city': '021',
            'citylimit': 'true',
            'output': 'json',
            'page': '',
        }
        future_to_url = {executor.submit(load_url, url, merge_dicts(param, {'page': i}), 60): url for i in range(1, 46)}
        for future in futures.as_completed(future_to_url):
            if future.exception() is not None:
                print future.exception()
            elif future.done():
                data = future.result()['pois']
                allloc.extend([x['location'] for x in data])
        with open('allloc1.pk', 'wb') as f:
            pickle.dump(allloc, f, True)


def merge_dicts(*dict_args):
    u'''
   可以接收1个或多个字典参数
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def mobai(loc):
    allmobai = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        url = 'https://mwx.mobike.com/mobike-api/rent/nearbyBikesInfo.do'
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E304 MicroMessenger/6.5.7 NetType/WIFI Language/zh_CN',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://servicewechat.com/wx80f809371ae33eda/23/page-frame.html',
        }
        data = {
            'longitude': '',
            'latitude': '',
            'citycode': '021',
        }
        future_to_url = {
            executor.submit(load_url, url, merge_dicts(data, {'longitude': i.split(',')[0]}, {'latitude': i.split(',')[1]}),
                            60,headers): url for i in loc}
        for future in futures.as_completed(future_to_url):
            if future.exception() is not None:
                print future.exception()
            elif future.done():
                data = future.result()['object']
                allmobai.extend(data)
                # 存入mongodb
                result = collection.insert_many(data)
if __name__ == '__main__':
    f = open('allloc.pk','rb')
    allloc = pickle.load(f)
    f.close()
    # print
    mobai(allloc)
