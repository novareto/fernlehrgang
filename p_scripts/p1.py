# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de


from sqlalchemy.orm import joinedload
from z3c.saconfig import Session
from fernlehrgang import models
from profilehooks import profile
from zope.component.hooks import setSite
from fernlehrgang.interfaces.resultate import ICalculateResults


def init(app, root):
    portal = root['flg']
    setSite(portal)
    session = Session()
    session.query(models.Fernlehrgang).all()



@profile
def worker(app, root):
    portal = root['flg']
    setSite(portal)
    session = Session()
    constraint = "%%%s%%" % "Kroos"
    sql = session.query(models.Kursteilnehmer, models.Teilnehmer).options(joinedload(models.Kursteilnehmer.antworten))
    sql = sql.filter(models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id)
    sql = sql.filter(models.Teilnehmer.name.ilike(constraint))

    for ktn, tn in sql.all():
        print ktn, tn
        summary = ICalculateResults(ktn).summary()



if __name__ == "__main__":
    init(app, root)
    worker(app, root)
    exit()

