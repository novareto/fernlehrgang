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
    T7 = JETZT - timedelta(days=7)
    T42 = JETZT - timedelta(days=42)
    T90 = JETZT - timedelta(days=90)
    T120 = JETZT - timedelta(days=120)
    T200 = JETZT - timedelta(days=200)
    return JETZT, T7, T42, T90, T120, T200


class BN(grok.View):
    grok.context(interface.Interface)
    grok.require('zope.Public')

    def __init__(self, datum, test):
        self.datum = datum
        self.test = test

    def update(self):
        MAILS = [] 
        JETZT, T7, T42, T90, T120, T200  = time_ranges(self.datum)
        logger.info("Jetzt: %s, 7T: %s, 42T: %s, 90T: %s, 120T: %s" % (JETZT, T7, T42, T90, T120))
        session = Session()
        alle_ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Kursteilnehmer.status.in_(('A1', 'A2')),
            models.Kursteilnehmer.erstell_datum > T200,
            models.Fernlehrgang.typ == '4')
        print(alle_ktns.count())
        with click.progressbar(alle_ktns.all()) as alle:
            for ktn in alle:
                #if ktn.fernlehrgang.id != 128:
                    erstell_datum = ktn.erstell_datum.date()
                    if erstell_datum < ktn.fernlehrgang.beginn:
                        erstell_datum = ktn.fernlehrgang.beginn
                    titel = ""
                    if ktn.teilnehmer.titel:
                        titel = ITeilnehmer['titel'].vocabulary.getTerm(ktn.teilnehmer.titel).title
                    if titel == "kein Titel":
                        titel = ""
                    #print "KTN %s - %s" %(ktn.id, erstell_datum)
                    if erstell_datum == T7 and len(ktn.antworten) == 0:
                        BETREFF = "Registrierung - Online-Fernlehrgang der BGHW, Benutzer-Nr. %s" % ktn.teilnehmer.id
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="7T",
                            text = mt.TEXTVLW01N % (
                                ktn.teilnehmer.vorname,
                                ktn.teilnehmer.name
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="E-Mail 0 Mon., Erinnerung 1",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                    elif erstell_datum == T42 and len(ktn.antworten) == 0:
                        BETREFF = "Erinnerung - Teilnahme am Online-Fernlehrgang der BGHW, Benutzer-Nr. %s" % ktn.teilnehmer.id
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="42T",
                            text = mt.TEXTVLW02N % (
                                ktn.teilnehmer.vorname,
                                ktn.teilnehmer.name,
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="E-Mail 1,5 Mon., Erinnerung 2",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                    elif erstell_datum == T90 and len(ktn.antworten) == 0:
                        BETREFF = "Ablauf der Frist und Fristverlängerung – Fernlehrgang der BGHW, Benutzer-Nr. %s" % ktn.teilnehmer.id
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="90T",
                            text = mt.TEXTVLW03N % (
                                ktn.teilnehmer.vorname,
                                ktn.teilnehmer.name
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="E-Mail 3 Mon., Fristverlängerung",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                    elif erstell_datum == T120 and len(ktn.antworten) == 0:
                        BETREFF = "Sperrung Fernlehrgang und Nachweis Regelbetreuung – Fernlehrgang der BGHW, Benutzer-Nr. %s" % ktn.teilnehmer.id
                        MAILS.append(dict(
                            _from='fernlehrgang.bghw.de',
                            _to=ktn.teilnehmer.email or 'ck@novareto.de',
                            subject=BETREFF,
                            reason="120T",
                            text = mt.TEXTVLW04N % (
                                ktn.teilnehmer.vorname,
                                ktn.teilnehmer.name
                            )
                            ))
                        ktn.teilnehmer.journal_entries.append(
                                models.JournalEntry(
                                    status="info",
                                    type="E-Mail 4 Mon., Sperre Fernlehrgang",
                                    kursteilnehmer_id=ktn.id,
                                    teilnehmer_id=ktn.teilnehmer.id)
                                )
                        ktn.status = "Z1"
        print(len(MAILS))
        for mail in MAILS:
            logger.info("SendMail: %s, %s %s" % (mail['_to'], mail['subject'], mail['reason']))
            if mail['_to'] == "b.sappich@bghw.de":
                send_mail('fernlehrgang@bghw.de', (mail['_to'], 'ck@novareto.de'), mail['subject'], mail['text'])
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
