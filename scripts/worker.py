# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


from zope import component
from z3c.saconfig import Session
from fernlehrgang import models


def worker():
    flg = root['app']
    component.hooks.setSite(flg)
    session = Session()
    fernlehrgang = session.query(models.Fernlehrgang).get(114)
    for i, ktn in enumerate(fernlehrgang.kursteilnehmer):
        print "%s, %s, %s" %(i, ktn.id, ktn.result)
    import transaction; transaction.commit()



if __name__ == "__main__":
    worker()
    exit()
