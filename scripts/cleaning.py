# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import csv
import click
import transaction

from fernlehrgang import models
from z3c.saconfig import Session
from zope.component.hooks import setSite
from fernlehrgang.interfaces.teilnehmer import generatePassword
from fernlehrgang.interfaces.cusa_result import ICusaResult


def worker(app, root):
    #flg = root['app']
    setSite(root)
    session = Session()
    ktns = session.query(models.Kursteilnehmer).filter(
        models.Kursteilnehmer.status != 'A1'
    )
    i=0
    for ktn in ktns:
        if len(ktn.antworten) > 0:
            mnr = ""
            if ktn.unternehmen:
                mnr = ktn.unternehmen.mnr
            print(ktn.id, ktn.fernlehrgang_id, ktn.teilnehmer.name, mnr)
        i += 1
    print(i)

if __name__ == "__main__":
    worker(app, root)
    exit()
