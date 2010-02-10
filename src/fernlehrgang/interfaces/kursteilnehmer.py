# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

def vocabulary(*terms):
    """ """
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])

class IKursteilnehmer(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des Teilnehmers für den Fernlehrgang',
        required = False,
        readonly = True
        )

    teilnehmer_id = Choice(
        title = u'Id des Teilnehmers',
        description = u'Die Eindeutige Nummer des Teilnehmers',
        required = True,
        vocabulary = 'unternehmen', 
        )

    status = Choice(
        title = u"Status",
        description = u"Bitte geben Sie in diesen Feld den Status des Teilnehmers ein",
        required = True,
        default = 1,
        vocabulary = vocabulary(
            (1, 'aktiv', 'aktiv'),
            (2, 'nicht registriert', 'nicht registriert'),
            (3, 'beendet', 'beendet'),)
        )
