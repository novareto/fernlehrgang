# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 


def page_query(q):
    offset = 0
    while True:
        r = False
        for a,b,c in q.limit(1000).offset(offset):
           r = True
           yield a,b,c 
        offset += 1000
        print offset
        if not r:
            break
