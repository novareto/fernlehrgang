# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


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
        vocabulary = "ReduceFrageVocab",
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
        vocabulary=vocabulary((1,1,1),(2,2,2),),
        )

