# coding: utf-8
import requests
from parsel import Selector
import js2xml

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept':'application/json',
    'X-Request':'JSON',
    'X-Requested-With':'XMLHttpRequest'
}

url = 'http://huaban.com/favorite/beauty/'

params = {
    'max':'',
    'limit':'100'
}

# z = requests.get(url,params=params,headers=headers)
# print z.json()

def getpins():
    z = requests.get(url,params=params,headers=headers)
    for i in z.json()['pins']:
        print i['pin_id']
    while True:
        last_pin_id = z.json()['pins'][-1]['pin_id']
        try:
            params['max'] = last_pin_id
            z = requests.get(url,params=params,headers=headers)
            for x in z.json()['pins']:
                print x['pin_id']
            last_pin_id = z.json()['pins'][-1]['pin_id']
        except:
            break
            
# 获取图片地址
def getimgsrc(pin_id):
    url = 'http://huaban.com/pins/%s/' % pin_id
    z = requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
    sel = Selector(text=z.text)
    jscode = sel.xpath("//script[contains(., 'app.page = app.page')]/text()").extract_first()
    parsed_js = js2xml.parse(jscode)
    for i in parsed_js.xpath('//property[@name="pins"]//property[@name="key"]/string/text()'):
        print 'http://img.hb.aicdn.com/' + i
        
# 下载图片
def downloadimg(url):
    z = requests.get(url)
    imgname = url.split('/')[-1]
    with open('%s.jpg' % imgname,'wb') as img:
        img.write(z.content)
        
if __name__ == '__main__':
    # getimgsrc('1094436033')
    downloadimg('http://img.hb.aicdn.com/70c2039b6492a3140fe3ef9a9ff98bdbab3a9b0f47f14-yP20CC')