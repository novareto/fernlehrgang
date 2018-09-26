# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


from zope import component
from z3c.saconfig import Session
from fernlehrgang import models
from datetime import datetime


dt = datetime(2016,1,1)
#dt = datetime.now()
print dt.date()


def worker():
    flg = root['app']
    component.hooks.setSite(flg)
    session = Session()
    ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == 103,
            models.Antwort.kursteilnehmer_id == models.Kursteilnehmer.id,
            models.Antwort.datum > dt )
    print ktns 
    for x in ktns.all():
        print x



if __name__ == "__main__":
    worker()
    exit()
