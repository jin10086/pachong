# -*- coding: utf-8 -*-
from lundaig import zhihudaiguang,vote_up

if __name__ == '__main__':
    all = zhihudaiguang.objects.filter(is_vote_up=0)
    
