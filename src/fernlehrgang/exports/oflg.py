# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import datetime

from fernlehrgang import models
from sqlalchemy import and_, not_
from sqlalchemy import func


def report(session):
    now = datetime.datetime.now()
    t = session.query(models.Antwort.kursteilnehmer_id).filter(and_(
        models.Lehrheft.fernlehrgang_id == '111',
        models.Lehrheft.id == models.Antwort.lehrheft_id))
    query = session.query(models.Kursteilnehmer)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == '111',
            models.Kursteilnehmer.erstell_datum > now - datetime.timedelta(weeks=(4*7)),
            models.Kursteilnehmer.erstell_datum < now - datetime.timedelta(weeks=(4*6)),
        )
    )

    # Keine Lehrhefte im Zeitraum
    print "-" * 44
    print "Keine Lehrhefte im Zeitraum"


    no_answers = query.filter(
            not_(models.Kursteilnehmer.id.in_(t)),
            #models.Antwort.lehrheft_id == models.Lehrheft.id,
            #models.Lehrheft.nummer < 4,
        )
    for x in no_answers.all():
        print x, x.teilnehmer
    print no_answers.count()


    print 
    print "-" * 44
    print "4.Lehrheft noch nicht beendet"
    not_finished = query.filter(
        and_(
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            models.Lehrheft.nummer < 4,
        )
    )
    for x in not_finished.all():
        print x, x.teilnehmer
    print not_finished.count()
    print
    print "-" * 44
    print "Mehr als 4.Lehrheft beendet"

    almost_finished = query.filter(
        and_(
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            models.Lehrheft.nummer > 4,
            models.Lehrheft.nummer < 8,
        )
    )
    for x in almost_finished.all():
        print x, x.teilnehmer
    print almost_finished.count()

    print
    print "-" * 44
    print "11 Monate weninger als 8 Lehrhefte"


    query = session.query(models.Kursteilnehmer)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == '111',
            models.Kursteilnehmer.erstell_datum > now - datetime.timedelta(weeks=(4*11)),
            models.Kursteilnehmer.erstell_datum < now - datetime.timedelta(weeks=(4*10)),
        )
    )
    almost_finished = query.filter(
        and_(
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            models.Lehrheft.nummer < 8,
        )
    )
    for x in almost_finished.all():
        print x, x.teilnehmer
    print almost_finished.count()


    print
    print "-" * 44
    print "> 12 Monate weninger als 8 Lehrhefte"

    query = session.query(models.Kursteilnehmer)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == '111',
            models.Kursteilnehmer.erstell_datum < now - datetime.timedelta(weeks=(4*12)),
        )
    )
    almost_finished = query.filter(
        and_(
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            models.Lehrheft.nummer < 8,
        )
    )
    for x in almost_finished.all():
        print x, x.teilnehmer
    print almost_finished.count()
