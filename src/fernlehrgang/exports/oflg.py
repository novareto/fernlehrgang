# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grok
import datetime

from dolmen.menu import menuentry
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.exports.menus import ExportItems

from fernlehrgang import models
from sqlalchemy import and_, not_
from sqlalchemy import func
from fernlehrgang.lib.mt import TEXT1, TEXT2, TEXT3, TEXT4
from fernlehrgang.lib.emailer import send_mail


def report(session):
    now = datetime.datetime.now()
    t = session.query(models.Antwort.kursteilnehmer_id).filter(and_(
        models.Lehrheft.fernlehrgang_id == '112',
        models.Lehrheft.id == models.Antwort.lehrheft_id))
    query = session.query(models.Kursteilnehmer)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == '112',
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
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email,],  # x.teilnehmer.email,
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT1 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )
    #print no_answers.count()


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
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email,],  # x.teilnehmer.email,
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT2 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )
        #print TEXT1 % (
        #    ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title,
        #    ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
        #    teilnehmer.name)
    #print not_finished.count()
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
            models.Kursteilnehmer.fernlehrgang_id == '112',
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
        titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
        if titel == "kein Titel":
            titel = ""
        send_mail(
            'fernlehrgang@bghw.de',
            [x.teilnehmer.email,],  # x.teilnehmer.email,
            'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
            text = TEXT3 % (
                titel,
                ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                x.teilnehmer.name
                )
            )
        #print TEXT2 % (
        #    ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title,
        #    ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
        #    teilnehmer.name)
    print almost_finished.count()


    print
    print "-" * 44
    print "> 12 Monate weninger als 8 Lehrhefte"

    query = session.query(models.Kursteilnehmer)
    query = query.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == '112',
            models.Kursteilnehmer.erstell_datum < now - datetime.timedelta(weeks=(4*12)),
            models.Kursteilnehmer.erstell_datum > now - datetime.timedelta(weeks=(4*13)),
        )
    )
    #print query.count()
    for x in query.all():
        print x, x.teilnehmer

    #import pdb; pdb.set_trace() 

    #almost_finished = query.filter(
    #    and_(
    #        models.Kursteilnehmer.id == models.Antwort.kursteilnehmer_id,
    #        models.Antwort.lehrheft_id == models.Lehrheft.id,
    #        models.Lehrheft.nummer != 8,
    #    )
    #)
    #for x in almost_finished.all():
        print x.teilnehmer.name
        if len(x.antworten) < 80:
            titel = ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title
            if titel == "kein Titel":
                titel = ""
            send_mail(
                'fernlehrgang@bghw.de',
                [x.teilnehmer.email,],  # x.teilnehmer.email,
                'Online-Fernlehrgang der BGHW Benutzername: %s' % x.teilnehmer.id,
                text = TEXT4 % (
                    titel,
                    ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
                    x.teilnehmer.name
                    )
                )
        #print unicode(TEXT3).encode('utf-8') % (
        #    ITeilnehmer['titel'].vocabulary.getTerm(x.teilnehmer.titel).title,
        #    ITeilnehmer['anrede'].vocabulary.getTerm(x.teilnehmer.anrede).title,
        #    x.teilnehmer.name)
    #print almost_finished.count()
    
@menuentry(ExportItems)
class OFLG_Report(grok.View):
    grok.context(IFernlehrgang)
    grok.name('oflg_report')
    grok.title('Report Online Fernlehrgang')

    def update(self):
        from fernlehrgang.tasks import notifications_for_ofg 
        #mail = getUserEmail(self.request.principal.id)
        stat = notifications_for_ofg()
        print stat 

    def render(self):
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
