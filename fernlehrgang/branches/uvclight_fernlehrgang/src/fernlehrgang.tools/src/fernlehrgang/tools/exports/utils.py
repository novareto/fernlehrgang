# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 


from os import system
from fernlehrgang.app.auth.handler import USERS


def getUserEmail(pid):
    return 'ck@novareto.de'
    return USERS.get(pid).email


def makeZipFile(fn):
    fnz = "%s.zip" % fn.split('.')[0]
    befehl = "zip -j -e -P fernlehrgang %s %s" %(fnz, fn)
    system(befehl)
    return fnz


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
