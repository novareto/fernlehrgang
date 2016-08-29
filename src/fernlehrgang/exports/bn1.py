# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import grok

from zope import interface
from datetime import datetime
from datetime import timedelta
from fernlehrgang import models
from z3c.saconfig import Session


JETZT = datetime.now()
T30 = JETZT - timedelta(days=30)
T180 = JETZT - timedelta(days=180)
T300 = JETZT - timedelta(days=300)
T365 = JETZT - timedelta(days=365)


print "JETZT", JETZT
print "T30", T30
print "T180", T180
print "T300", T300
print "T365", T365


MAILS = [] 


class BN1(grok.View):
    grok.context(interface.Interface)

    def update(self):
        session = Session()
        alle_ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Fernlehrgang.typ == '2')

        for ktn in alle_ktns.all():
            erstell_datum = ktn.erstell_datum.date()
            print "KTN %s - %s" %(ktn.id, erstell_datum)
            BETREFF = "BENACHRICHTIGUNG 30 Tage - Keine Antworten"
            if erstell_datum == T30.date() and len(ktn.antworten) == 0:
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=u"TEST"
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
                BETREFF="180 TAGE NIX"
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=u"TEST"
                    ))
                ktn.teilnehmer.journal_entries.append(
                        models.JournalEntry(
                            status="info",
                            type="BETREFF",
                            kursteilnehmer_id=ktn.id,
                            teilnehmer_id=ktn.teilnehmer.id)
                        )
            elif erstell_datum == T180.date() and len(ktn.antworten) <= 40:
                BETREFF="180 TAGE LH 1-4"
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=u"TEST"
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
                BETREFF="380 TAGE LH 1-4"
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=u"TEST"
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
                BETREFF="356 nicht FERTIG"
                MAILS.append(dict(
                    _from='fernlehrgang.bghw.de',
                    _to=ktn.teilnehmer.email or 'ck@novareto.de',
                    subject=BETREFF,
                    text=u"TEST"
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
                print mail

    def render(self):
        return u"HALLO WELT"
