# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

from sqlalchemy import and_
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
    FERNLEHRGANG_ID = 140
    sql = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer)
    sql = sql.options(joinedload(models.Kursteilnehmer.antworten))
    sql = sql.options(joinedload(models.Kursteilnehmer.fernlehrgang))
    sql = sql.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == FERNLEHRGANG_ID,
            models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
            models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)

    for tn, unt, ktn in sql.all():
        print ktn, tn, unt
        import pdb; pdb.set_trace()
        summary = ICalculateResults(ktn).summary()



if __name__ == "__main__":
    init(app, root)
    worker(app, root)
    exit()

