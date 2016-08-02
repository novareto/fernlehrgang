# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grok
import datetime
import sqlalchemy

from dolmen.menu import menuentry
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.exports.menus import ExportItems

from fernlehrgang import models
from sqlalchemy import and_, not_
from sqlalchemy import func
from fernlehrgang.lib.mt import TEXT1, TEXT2, TEXT3, TEXT4
from fernlehrgang.lib.emailer import send_mail


def send_mail(f, t, s, text):  ## REMOVE the _ (underscore to prevent sending mails)
    print "#"*55
    print f
    print t
    print s
    print text
    print "#"*55
    print 


def report(session):
    now = datetime.datetime.now()
    t = session.query(models.Antwort.kursteilnehmer_id).filter(and_(
        models.Lehrheft.fernlehrgang_id == models.Fernlehrgang.id,
        models.Fernlehrgang.typ == "2",
        models.Lehrheft.id == models.Antwort.lehrheft_id))

    # 30 TAGE
    query = session.query(models.Kursteilnehmer)
    vgdatum = now - datetime.timedelta(days=180)
    print vgdatum
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Fernlehrgang.typ == "2",
            sqlalchemy.sql.expression.cast(models.Kursteilnehmer.erstell_datum, sqlalchemy.types.Date) == vgdatum.date(),
        )
    )

    # Keine Lehrhefte im Zeitraum
    print "-" * 44
    print "Keine Lehrhefte im Zeitraum"
    print query.count()

    no_answers = query.filter(
            not_(models.Kursteilnehmer.id.in_(t)),
        )
    for x in no_answers.all():
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email, 'fernlehrgangemail@bghw.de'],
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT1 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )

    #

    query = session.query(models.Kursteilnehmer)
    vgdatum = now - datetime.timedelta(days=30)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Fernlehrgang.typ == "2",
            sqlalchemy.sql.expression.cast(models.Kursteilnehmer.erstell_datum, sqlalchemy.types.Date) == vgdatum.date(),
        )
    )

    # Keine Lehrhefte im Zeitraum
    print "-" * 44
    print "Keine Lehrhefte im Zeitraum"
    print query.count()

    no_answers = query.filter(
            not_(models.Kursteilnehmer.id.in_(t)),
        )
    for x in no_answers.all():
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email, 'fernlehrgangemail@bghw.de'],
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT1 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )


    print 
    print "-" * 44
    print "4.Lehrheft noch nicht beendet"
    not_finished = query.filter(
        and_(
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            models.Lehrheft.nummer.in_(('1','2','3','4')), 
            models.Lehrheft.nummer.notin_(('5','6','7','8')) 
        )
    )
    for x in not_finished.all():
        print x, x.teilnehmer
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email, 'fernlehrgangemail@bghw.de'],
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT2 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )
    #print
    #print "-" * 44
    #print "Mehr als 4.Lehrheft beendet"
    #almost_finished = query.filter(
    #    and_(
    #        models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
    #        models.Antwort.lehrheft_id == models.Lehrheft.id,
    #        models.Lehrheft.nummer > 4,
    #        models.Lehrheft.nummer < 8,
    #    )
    #)
    #for x in almost_finished.all():
    #    print x, x.teilnehmer
    #print almost_finished.count()

    print
    print "-" * 44
    print "11 Monate weninger als 8 Lehrhefte"


    query = session.query(models.Kursteilnehmer)
    vgdatum = now - datetime.timedelta(days=300)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Fernlehrgang.typ == "2",
            sqlalchemy.sql.expression.cast(models.Kursteilnehmer.erstell_datum, sqlalchemy.types.Date) == vgdatum.date(),
        )
    )
    almost_finished = query.filter(
        and_(
            models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
            models.Antwort.lehrheft_id == models.Lehrheft.id,
            sqlalchemy.sql.expression.cast(models.Lehrheft.nummer, sqlalchemy.types.Integer) < 8,
        )
    )
    for x in almost_finished.all():
        print x, x.teilnehmer
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email, 'fernlehrgangemail@bghw.de'],
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT3 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )


    print
    print "-" * 44
    print "> 12 Monate weninger als 8 Lehrhefte"

    query = session.query(models.Kursteilnehmer)
    vgdatum = now - datetime.timedelta(days=365)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Fernlehrgang.typ == "2",
            sqlalchemy.sql.expression.cast(models.Kursteilnehmer.erstell_datum, sqlalchemy.types.Date) == vgdatum.date(),
        )
    )
    for ktn in query.all():
        if len(ktn.antworten) < 80:
            titel = ITeilnehmer['titel'].vocabulary.getTerm(ktn.teilnehmer.titel).title
            if titel == "kein Titel":
                titel = ""
            send_mail(
                'fernlehrgang@bghw.de',
                [ktn.teilnehmer.email, 'fernlehrgangemail@bghw.de'],
                'Online-Fernlehrgang der BGHW Benutzername: %s' % ktn.teilnehmer.id,
                text = TEXT4 % (
                    titel,
                    ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                    ktn.teilnehmer.name
                    )
                )
            ktn.status = "Z1"
    

#@menuentry(ExportItems)
class OFLG_Report(grok.View):
    grok.context(IFernlehrgang)
    grok.name('oflg_report')
    grok.title('Report Online Fernlehrgang')
    grok.require('zope.Public')

    def update(self):
        from z3c.saconfig import Session
        report(Session())

    def render(self):
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
