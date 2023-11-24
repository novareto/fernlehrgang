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
    q_unternehmen = session.query(models.Unternehmen).filter(models.Unternehmen.mnr.startswith('9'))
    i = 1
    print (q_unternehmen.count())
    sp_range = [x for x in range(0, 500000, 1000)]
    for unternehmen in q_unternehmen.all():
        if i in sp_range:
            print(i)
            sp = transaction.savepoint()
        ICusaResult(unternehmen).persist()
        i += 1
    transaction.commit()

if __name__ == "__main__":
    worker(app, root)
    exit()
