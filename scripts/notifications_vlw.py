# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import grok
import click
import logging

from zope import interface
from datetime import datetime
from datetime import timedelta
from fernlehrgang import models
from fernlehrgang import log
from z3c.saconfig import Session
from fernlehrgang.lib import mt
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.lib.emailer import send_mail

logger = logging.getLogger('fernlehrgang.notification_vlw')


def time_ranges(JETZT):
    T30 = JETZT - timedelta(days=30)
    T180 = JETZT - timedelta(days=180)
    T300 = JETZT - timedelta(days=300)
    T365 = JETZT - timedelta(days=365)
    T380 = JETZT - timedelta(days=380)
    return JETZT, T30, T180, T300, T365, T380


class BN(grok.View):
    grok.context(interface.Interface)
    grok.require('zope.Public')

    def __init__(self, datum, test):
        self.datum = datum
        self.test = test

    def update(self):
        MAILS = [] 
        JETZT, T30, T180, T300, T365, T380 = time_ranges(self.datum)
        logger.info("Jetzt: %s, 30T: %s, 180T: %s, 300T: %s, 365T: %s" % (JETZT, T30, T180, T300, T365))
        session = Session()
        alle_ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Kursteilnehmer.status.in_(('A1', 'A2')),
            models.Kursteilnehmer.erstell_datum > T380,
            models.Fernlehrgang.typ == '4')
        print(alle_ktns.count())
        with click.progressbar(alle_ktns.all()) as alle:
            for ktn in alle:
                if ktn.fernlehrgang.id != 128:
                    erstell_datum = ktn.erstell_datum.date()
                    if erstell_datum < ktn.fernlehrgang.beginn:
                        erstell_datum = ktn.fernlehrgang.beginn
                    titel = ""
                    if ktn.teilnehmer.titel:
                        titel = ITeilnehmer['titel'].vocabulary.getTerm(ktn.teilnehmer.titel).title
                    if titel == "kein Titel":
                        titel = ""
                    BETREFF = "Online-Fernlehrgang der BGHW Benutzername %s" % ktn.teilnehmer.id
                    #print "KTN %s - %s" %(ktn.id, erstell_datum)
                    if erstell_datum == T30 and len(ktn.antworten) == 0:
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="30T",
                            text = mt.TEXTVLW01 % (
                                titel,
                                ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                                ktn.teilnehmer.name,
                                ktn.teilnehmer.id
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="MAIL-Report 30 Tage",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                    elif erstell_datum == T180 and len(ktn.antworten) == 0:
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="180T",
                            text = mt.TEXTVLW02 % (
                                titel,
                                ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                                ktn.teilnehmer.name,
                                ktn.teilnehmer.id
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="MAIL REPORT 180 Tage ",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                    elif erstell_datum == T365 and len(ktn.antworten) == 0:
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="365T",
                            text = mt.TEXTVLW03 % (
                                titel,
                                ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                                ktn.teilnehmer.name
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="MAIL 365T",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                        ktn.status = "Z1"
        print(len(MAILS))
        for mail in MAILS:
            logger.info("SendMail: %s, %s %s" % (mail['_to'], mail['subject'], mail['reason']))
            send_mail('fernlehrgang@bghw.de', (mail['_to'],), mail['subject'], mail['text'])
            #send_mail('fernlehrgang@bghw.de', ('ck@novareto.de',), mail['subject'], mail['text'])

        if not self.test:
            import transaction; transaction.commit()
            print("commit")


@click.command()
@click.option('--datum', default=None, help='Datum')
@click.option('--test', default=False, help='Datum')
def doit(datum, test):
    if datum:
        datum = datetime.strptime(datum, "%d.%m.%Y").date()
    else:
        datum = datetime.now().date()
    try:
        logger.info('Start Notifcation RUN %s' % datum)
        bn1 = BN(datum, test)
        bn1.update()
    except:
        logger.exception('FEHLER')


if __name__ == "__main__":
    doit()
    exit()
