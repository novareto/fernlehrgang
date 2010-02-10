# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface

class IAntwort(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung der Antwort',
        required = False,
        readonly = True
        )

    lehrheft_id = Choice(
        title = u'Lehrheft',
        description = u'Für welches Lehrheft liegt eine Antwort vor.',
        required = True,
        vocabulary = "LehrheftVocab",
        )

    frage_id = Choice(
        title = u'Frage',
        description = u'Für welche Frage soll das Antwortschema sein.',
        required = True,
        vocabulary = "FragenVocab",
        )

    antwortschema = TextLine(
        title = u'Antwortschema',
        description = u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required = True,
        )

