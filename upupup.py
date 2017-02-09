# -*- coding: utf-8 -*-
import time
from lundaig import zhihudaiguang,vote_up
import requests
if __name__ == '__main__':
    alllist = zhihudaiguang.objects.filter(is_sex=1).filter(is_vote_up=0).only('id')
    while 1:
        if alllist.count() == 0:
            time.sleep(10*60)
        else:
            for i in alllist:
                vote_up(i.id)
                i.is_vote_up = True
                i.save()
                time.sleep(2*60)