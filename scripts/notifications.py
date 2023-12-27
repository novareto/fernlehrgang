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
from z3c.saconfig import Session
from fernlehrgang.lib import mt
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.lib.emailer import send_mail
from sqlalchemy import Date, not_, cast, case, literal_column, func, update


logger = logging.getLogger('notifications')


def casing(JETZT):
    T30 = JETZT - timedelta(days=30)
    T180 = JETZT - timedelta(days=180)
    T300 = JETZT - timedelta(days=300)
    T365 = JETZT - timedelta(days=365)

    print(T30, T180, T300, T365)

    return case(
        (
            cast(models.Kursteilnehmer.erstell_datum, Date) == T30,
            literal_column("'T30'")
        ),
        (
            cast(models.Kursteilnehmer.erstell_datum, Date) == T180,
            literal_column("'T180'")
        ),
        (
            cast(models.Kursteilnehmer.erstell_datum, Date) == T300,
            literal_column("'T300'")
        ),
        (
            cast(models.Kursteilnehmer.erstell_datum, Date) == T365,
            literal_column("'T365'")
        ),
        else_=literal_column("'other'")
    ), cast(models.Kursteilnehmer.erstell_datum, Date).in_((T30, T180, T300, T365))



class BNTest(grok.View):
    grok.context(interface.Interface)
    grok.require('zope.Public')

    def __init__(self, datum, test):
        self.datum = datum
        self.test = test

    def update(self):
        MAILS = []
        session = Session()
        cases, where = casing(self.datum)
        alle_ktns = session.query(
            models.Kursteilnehmer.id.label('ktn_id'),
            models.Teilnehmer.id.label('tn_id'),
            models.Teilnehmer.name.label('name'),
            models.Teilnehmer.anrede.label('anrede'),
            models.Teilnehmer.email.label('email'),
            models.Teilnehmer.titel.label('titel'),
            cases.label("diff"),
            func.count(models.Antwort.id).label('counter')
        ).group_by(
            models.Kursteilnehmer.id, models.Teilnehmer.id
        ).join(
            models.Antwort,
            models.Antwort.kursteilnehmer_id == models.Kursteilnehmer.id,
            isouter=True
        ).filter(
            models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang.id,
            models.Kursteilnehmer.status.in_(('A1', 'A2')),
            models.Fernlehrgang.typ == '2', where)
        print(alle_ktns)
        found = alle_ktns.all()
        import pdb; pdb.set_trace()
        with click.progressbar(found) as alle:
            for row in alle:
                try:
                    titel = ITeilnehmer['titel'].vocabulary.getTerm(
                        row.titel
                    ).title
                    if titel == "kein Titel":
                        titel = ""
                except:
                    titel = ""
                BETREFF = 'Online-Fernlehrgang der BGHW Benutzername: %s' % row.tn_id

                if row.diff == 'T30' and row.counter == 0:
                    MAILS.append(dict(
                        _from='fernlehrgang.bghw.de',
                        _to=row.email or 'ck@novareto.de',
                        tid=row.tn_id,
                        subject=BETREFF,
                        text=mt.TEXT0 % (
                            titel,
                            ITeilnehmer['anrede'].vocabulary.getTerm(row.anrede).title,
                            row.name
                        )
                    ))
                    session.add(
                        models.JournalEntry(
                            status="info",
                            type="EMAIL-Report 30 Tage",
                            kursteilnehmer_id=row.ktn_id,
                            teilnehmer_id=row.tn_id)
                    )
                elif row.diff == 'T180' and row.counter == 0:
                    MAILS.append(dict(
                        _from='fernlehrgang.bghw.de',
                        _to=row.email or 'ck@novareto.de',
                        subject=BETREFF,
                        tid=row.tn_id,
                        text=mt.TEXT1 % (
                            titel,
                            ITeilnehmer['anrede'].vocabulary.getTerm(row.anrede).title,
                            row.name
                        )
                    ))
                    session.add(
                        models.JournalEntry(
                            status="info",
                        type="EMAIL-Report 180 Tage, keine Antworten",
                            kursteilnehmer_id=row.ktn_id,
                            teilnehmer_id=row.tn_id)
                    )
                elif erstell_datum == T180 and row.counter <= 40:
                    MAILS.append(dict(
                        _from='fernlehrgang.bghw.de',
                        _to=row.email or 'ck@novareto.de',
                        subject=BETREFF,
                        tid=row.tn_id,
                        text=mt.TEXT2 % (
                            titel,
                            ITeilnehmer['anrede'].vocabulary.getTerm(row.anrede).title,
                            row.name
                        )
                    ))
                    session.add(
                        models.JournalEntry(
                            status="info",
                            type="EMAIL-Report 180 Tage, <= 4. Lehrheft",
                            kursteilnehmer_id=row.ktn_id,
                            teilnehmer_id=row.tn_id)
                    )
                elif erstell_datum == T300 and row.counter < 80:
                    MAILS.append(dict(
                        _from='fernlehrgang.bghw.de',
                        _to=row.email or 'ck@novareto.de',
                        subject=BETREFF,
                        tid=row.tn_id,
                        text=mt.TEXT3 % (
                            titel,
                            ITeilnehmer['anrede'].vocabulary.getTerm(row.anrede).title,
                            row.name
                        )
                    ))
                    session.add(
                        models.JournalEntry(
                            status="info",
                            type="EMAIL-Report 300 Tage und noch nicht fertig",
                            kursteilnehmer_id=row.ktn_id,
                            teilnehmer_id=row.tn_id)
                    )
                elif erstell_datum == T365 and row.counter < 80:
                    MAILS.append(dict(
                        _from='fernlehrgang.bghw.de',
                        _to=row.email or 'ck@novareto.de',
                        subject=BETREFF,
                        tid=row.tn_id,
                        text=mt.TEXT4 % (
                            titel,
                            ITeilnehmer['anrede'].vocabulary.getTerm(row.anrede).title,
                            row.name
                        )
                    ))
                    session.add(
                        models.JournalEntry(
                            status="info",
                            type="EMAIL-Report 365 Tage",
                        kursteilnehmer_id=row.ktn_id,
                            teilnehmer_id=row.tn_id)
                    )
                    session.execute(
                        update(models.Kursteilnehmer).where(
                            Kursteilnehmer.id == row.ktn_id
                        ).values(status="Z1")
                    )

        for mail in MAILS:
            logger.info("SendMail: %s, %s, %s" % (mail['tid'], mail['_to'], mail['subject']))
            print("SendMail: %s, %s, %s" % (mail['tid'], mail['_to'], mail['subject']))
            send_mail('fernlehrgang@bghw.de', (mail['_to'], 'fernlehrgangemail@bghw.de'), mail['subject'], mail['text'])
            #send_mail('fernlehrgang@bghw.de', ('ck@novareto.de', 'fernlehrgangemail@bghw.de'), mail['subject'], mail['text'])

        if not self.test:
            import transaction; transaction.commit()


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
        bn1 = BNTest(datum, test)
        bn1.update()
    except:
        logger.exception('FEHLER')
        raise


if __name__ == "__main__":
    doit()
    exit()
