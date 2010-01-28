# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface

class IFrage(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des ResultatSets',
        required = False,
        readonly = True
        )

    frage = Int(
        title = u'Frage',
        description = u'Für welche Frage soll das Antwortschema sein.',
        required = True,
        )

    antwortschema = TextLine(
        title = u'Antwortschema',
        description = u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required = True,
        )

    eingangsdatum = Date(
        title = u'Eingangsdatum',
        description = u'Bitte geben Sie das Eingangsdatum der Antwort an.',
        required = True,
        )
