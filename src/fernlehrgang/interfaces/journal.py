# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

import grokcore.component as grok

from zope.schema import Int, TextLine, Choice, Datetime
from zope.interface import Interface

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@grok.provider(IContextSourceBinder)
def getKursteilnehmer(context):
    rc = []
    if IJournalEntry.providedBy(context):
        tn = context.teilnehmer
    else:
        tn = context
    for ktn in tn.kursteilnehmer:
        rc.append(
            SimpleTerm(
                ktn.id,
                ktn.id,
                "%s-%s %s" % (
                    ktn.fernlehrgang.titel,
                    ktn.fernlehrgang.jahr,
                    tn.name)
            )
        )
    return SimpleVocabulary(rc)


class TolerantVocabulary(SimpleVocabulary):

    def getTerm(self, v):
        try:
            return super(TolerantVocabulary, self).getTerm(v)
        except LookupError:
            return SimpleTerm(v, v, v)



@grok.provider(IContextSourceBinder)
def get_status(context):
    rc = [
        SimpleTerm('1', 'Info', u'Info'),
        SimpleTerm('2', 'Lernfortschritt', u'Lernfortschritt'),
        SimpleTerm('4', 'Abschluss Gespräch', u'Abschluss Gespräch'),
        SimpleTerm('5', 'Erinnerungsmail', u'Erinnerungsmail'),
        SimpleTerm('409', 'GBO nicht angelegt', u'GBO nicht angelegt. Eintrag schon vorhanden'),
        SimpleTerm('400', 'GBO uebertrag fehlerhaft', u'GBO Uebertrag war fehlerhaft'),
        SimpleTerm('1000', 'manuell geloest', u'Manuell gelöst'),
    ]
    return TolerantVocabulary(rc)


class IJournalEntry(Interface):

    status = Choice(
        title=u'Status',
        source=get_status,
        required=True,
    )

    type = TextLine(
        title=u'Type',
        required=True,
    )

    kursteilnehmer_id = Choice(
        title=u'Kursteilnehmer',
        required=True,
        source=getKursteilnehmer,
    )

    # Filled automatically
    id = TextLine(
        title=u'Unique identifier',
        required=True,
    )

    teilnehmer_id = Int(
        title=u'Teilnehmer',
        required=True,
    )

    date = Datetime(
        title=u'Date',
        required=True,
    )
