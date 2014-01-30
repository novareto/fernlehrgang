# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import datetime

from fernlehrgang import models
from sqlalchemy import and_
from sqlalchemy import func


def report(session):
    now = datetime.datetime.now()
    q = session.query(models.Kursteilnehmer, models.Lehrheft).filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == '110',
            models.Kursteilnehmer.id == '1103190',
            #models.Kursteilnehmer.erstell_datum > now - datetime.timedelta(weeks=(4*7)),
            #models.Kursteilnehmer.erstell_datum < now - datetime.timedelta(weeks=(4*6)),
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            models.Lehrheft.nummer > 4,
        )
    )
    for x, y in q.all():
        print x, y
    print q.count()
