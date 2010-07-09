# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

LIEFERSTOPPS = (('L1', u'UN-Modell anderer UV-Träger'),
                ('L2', u'Grund- bzw. Regelbetreuung'),
                ('L3', u'Keine Beschäftigten'),
                ('L4', u'Teilnahme aus pers. Gründen verschoben'),
                ('L5', u'Teilnahme ist bereits erfolgt'),
                ('L6', u'Aufgabe des Unternehmens'),
                ('A1', u'aktiv'),
                ('A2', u'nicht registriert'),
               ) 

class Lieferstopps(grok.GlobalUtility):
    grok.name('uvc.lieferstopps')
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        items = []
        for key, value in LIEFERSTOPPS:
            items.append(SimpleTerm(key, key, value))
        return SimpleVocabulary(items)


class IKursteilnehmer(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des Teilnehmers für den Fernlehrgang',
        required = False,
        readonly = True
        )

    teilnehmer_id = TextLine(
        title = u'Id des Teilnehmers',
        description = u'Die Eindeutige Nummer des Teilnehmers',
        required = True,
        )

    status = Choice(
        title = u"Status",
        description = u"Bitte geben Sie in diesen Feld den Status des Teilnehmers ein",
        required = True,
        default = '1',
        vocabulary = 'uvc.lieferstopps' 
        )
