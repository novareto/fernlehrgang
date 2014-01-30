# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grokcore.component as grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder


def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


@grok.provider(IContextSourceBinder)
def reduce_fragen(context):
    rc = []
    reduce = []
    alle = range(1, 11)
    from fernlehrgang.interfaces.lehrheft import ILehrheft
    if ILehrheft.providedBy(context):
        fragen = context.fragen
        reduce = [int(x.frage) for x in fragen]
    if IFrage.providedBy(context):
        fragen = context.lehrheft.fragen
    for x in alle:
        if x not in reduce:
            rc.append(SimpleTerm(str(x), str(x), str(x)))
    return SimpleVocabulary(rc)   


class IFrage(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des ResultatSets',
        required = False,
        readonly = True
        )

    frage = Choice(
        title = u'Frage',
        description = u'Für welche Frage soll das Antwortschema sein.',
        required = True,
        source = reduce_fragen,
        )

    titel = TextLine(
        title = u'Titel',
        description = u'Titel der Frage.',
        required = True,
        )

    antwortschema = TextLine(
        title = u'Antwortschema',
        description = u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required = True,
        )

    gewichtung = Choice(
        title = u'Gewichtung',
        description = u'Bitte geben Sie die Gewichtung für diese Frage ein.',
        required = True,
        vocabulary=vocabulary((2,2,2),(3,3,3),),
        )

