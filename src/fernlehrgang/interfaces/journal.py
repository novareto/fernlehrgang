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
    for ktn in context.kursteilnehmer:
        rc.append(
            SimpleTerm(
                ktn.id,
                ktn.id,
                "%s-%s %s" % (ktn.fernlehrgang.titel, ktn.fernlehrgang.jahr, teilnehmer.name)
            )
        )
    return SimpleVocabulary(rc)


class IJournalEntry(Interface):

    status = TextLine(
        title=u'Status',
        required=True,
    )

    type = TextLine(
        title=u'Status',
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
