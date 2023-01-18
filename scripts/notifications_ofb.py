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
from profilehooks import profile

logger = logging.getLogger('fernlehrgang.notification_ofb')


def time_ranges(JETZT):
    #JETZT = datetime.now()
    T30 = JETZT - timedelta(days=30)
    T180 = JETZT - timedelta(days=180)
    T300 = JETZT - timedelta(days=300)
    T365 = JETZT - timedelta(days=365)
    T600 = JETZT - timedelta(days=400)
    return JETZT, T30, T180, T300, T365, T600


class BN(grok.View):
    grok.context(interface.Interface)
    grok.require('zope.Public')

    def __init__(self, datum, test):
        self.datum = datum
        self.test = test

    #@profile
    def update(self):
        MAILS = [] 
        JETZT, T30, T180, T300, T365, T600 = time_ranges(self.datum)
        log("%s, %s, %s, %s, %s" % (JETZT, T30, T180, T300, T365))
        session = Session()
        alle_ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Kursteilnehmer.status.in_(('A1', 'A2')),
            models.Kursteilnehmer.erstell_datum > T600,
            models.Fernlehrgang.typ == '5')
        print(alle_ktns.count())
        with click.progressbar(alle_ktns.all()) as alle:
            for ktn in alle:
                    erstell_datum = ktn.erstell_datum.date()
                    if erstell_datum < ktn.fernlehrgang.beginn:
                        erstell_datum = ktn.fernlehrgang.beginn
                    titel = ""
                    if ktn.teilnehmer.titel:
                        titel = ITeilnehmer['titel'].vocabulary.getTerm(ktn.teilnehmer.titel).title
                    if titel == "kein Titel":
                        titel = ""
                    BETREFF = "Online-Fernlehrgang-Fortbildung der BGHW Benutzername %s" % ktn.teilnehmer.id
                    if erstell_datum == T30 and len(ktn.antworten) == 0:
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="30",
                            text = mt.TEXTFB1 % (
                                titel,
                                ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                                ktn.teilnehmer.name
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
                            reason="180",
                            text = mt.TEXTFB2 % (
                                titel,
                                ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                                ktn.teilnehmer.name
                                )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="MAIL REPORT 180 Tage ",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                    elif erstell_datum == T300 and len(ktn.antworten) == 0:
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="300",
                            text = mt.TEXTFB3 % (
                                titel,
                                ITeilnehmer['anrede'].vocabulary.getTerm(ktn.teilnehmer.anrede).title,
                                ktn.teilnehmer.name
                                )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="MAIL Report 300 Tage",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                            )
                    elif erstell_datum == T365 and len(ktn.antworten) == 0:
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="365",
                            text = mt.TEXTFB4 % (
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
                        print("356 TAGE")

        for mail in MAILS:
            logger.info("SendMail: %s, %si - %s" % (mail['_to'], mail['subject'], mail['reason']))
            send_mail('flg_app', (mail['_to'],), mail['subject'], mail['text'])

        #import pdb; pdb.set_trace()
        if not self.test:
            import transaction; transaction.commit()
            print('COMMIT')


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
