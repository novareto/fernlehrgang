# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 


from os import system
from zope.component import getUtility
from zope.pluggableauth.interfaces import IAuthenticatorPlugin


def getUserEmail(pid):
    ut = getUtility(IAuthenticatorPlugin, 'principals')
    return ut.getAccount(pid).getEmail()


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

def page_query_ktn(q):
    offset = 0
    while True:
        r = False
        for a in q.limit(1000).offset(offset):
           r = True
           yield a 
        offset += 1000
        print offset
        if not r:
            break
