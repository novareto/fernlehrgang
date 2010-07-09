# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from datetime import datetime

def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])

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

    datum = Datetime(
        title = u'Datum',
        description = u'Modifikationsdatum',
        required = True,
        readonly = True,
        default = datetime.now()
        )

    system = Choice(
        title = u'Eingabesystem',
        description = u'Bitte geben Sie an wie diese Antwort ins System gekommen ist.',
        required = True,
        vocabulary=vocabulary(('FernlehrgangApp', 'FernlehrgangApp', 'FernlehrgangApp'),
                              ('Extranet', 'Extranet', 'Extranet'),),
        )
