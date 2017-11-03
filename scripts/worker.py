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
    teilnehmer = session.query(models.Teilnehmer).get(101032)
    je = models.JournalEntry(type="kk", status="HH")
    teilnehmer.journal_entries.append(je)
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    worker()
    exit()
