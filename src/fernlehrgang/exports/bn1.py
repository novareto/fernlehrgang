# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import grok

from zope import interface
from datetime import datetime
from datetime import timedelta
from fernlehrgang import models
from z3c.saconfig import Session
from fernlehrgang.lib import mt
from .bn import time_ranges
from fernlehrgang import log
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.lib.emailer import send_mail


class BN1(grok.View):
    grok.context(interface.Interface)

    def update(self):
        MAILS = [] 
        JETZT, T30, T180, T300, T365 = time_ranges()
        log("%s, %s, %s, %s, %s" % (JETZT.date(), T30.date(), T180.date(), T300.date(), T365.date()))
        session = Session()
        alle_ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Fernlehrgang.typ == '2')

        for ktn in alle_ktns.all():
            erstell_datum = ktn.erstell_datum.date()
            titel = ITeilnehmer['titel'].vocabulary.getTerm(ktn.teilnehmer.titel).title
            if titel == "kein Titel":
                titel = ""
            print "KTN %s - %s" %(ktn.id, erstell_datum)
            BETREFF = 'Online-Fernlehrgang der BGHW Benutzername: %s' % ktn.teilnehmer.id,
            if erstell_datum == T30.date() and len(ktn.antworten) == 0:
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=mt.TEXT1 % (
                        titel,
                        ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                        ktn.teilnehmer.name
                    )
                    ))
                ktn.teilnehmer.journal_entries.append(
                        models.JournalEntry(
                            status="info",
                            type=BETREFF,
                            kursteilnehmer_id=ktn.id,
                            teilnehmer_id=ktn.teilnehmer.id)
                        )
                print "30 TAGE"
            elif erstell_datum == T180.date() and len(ktn.antworten) == 0:
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=mt.TEXT1 % (
                        titel,
                        ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                        ktn.teilnehmer.name
                    )
                    ))
                ktn.teilnehmer.journal_entries.append(
                        models.JournalEntry(
                            status="info",
                            type="BETREFF",
                            kursteilnehmer_id=ktn.id,
                            teilnehmer_id=ktn.teilnehmer.id)
                        )
            elif erstell_datum == T180.date() and len(ktn.antworten) <= 40:
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=mt.TEXT2 % (
                        titel,
                        ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                        ktn.teilnehmer.name
                    )
                    ))
                ktn.teilnehmer.journal_entries.append(
                        models.JournalEntry(
                            status="info",
                            type=BETREFF,
                            kursteilnehmer_id=ktn.id,
                            teilnehmer_id=ktn.teilnehmer.id)
                        )
                print "180 TAGE"
            elif erstell_datum == T300.date() and len(ktn.antworten) < 80:
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=mt.TEXT3 % (
                        titel,
                        ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                        ktn.teilnehmer.name
                    )
                    ))
                ktn.teilnehmer.journal_entries.append(
                        models.JournalEntry(
                            status="info",
                            type=BETREFF,
                            kursteilnehmer_id=ktn.id,
                            teilnehmer_id=ktn.teilnehmer.id)
                        )
                print "300 TAGE"
            elif erstell_datum == T365.date() and len(ktn.antworten) < 80:
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=mt.TEXT4 % (
                        titel,
                        ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                        ktn.teilnehmer.name
                    )
                    ))
                ktn.teilnehmer.journal_entries.append(
                        models.JournalEntry(
                            status="info",
                            type=BETREFF,
                            kursteilnehmer_id=ktn.id,
                            teilnehmer_id=ktn.teilnehmer.id)
                        )
                ktn.status = "Z1"
                print "356 TAGE"

            for mail in MAILS:
                send_mail('flg_app', (mail['_to'],), mail['subject'], mail['text'])

    def render(self):
        return u"HALLO WELT"
