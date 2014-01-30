# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

from zope.schema import *
from zope.interface import Interface, provider
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from . import named_vocabulary


LIEFERSTOPPS = (('L1', u'UN-Modell anderer UV-Träger'),
                ('L2', u'Grund- bzw. Regelbetreuung'),
                ('L3', u'Keine Beschäftigten'),
                ('L4', u'Teilnahme aus pers. Gründen verschoben'),
                ('L5', u'Teilnahme ist bereits erfolgt'),
                ('L6', u'Aufgabe des Unternehmens'),
                ('L7', u'Teilnehmer nicht mehr im Unternehmen'),
                ('S1', u'Interner Fehler'),
                ('A1', u'angemeldet'),
                ('A2', u'nicht registriert'),
               ) 


UN_KLASSE = (('G3', u'<= 10'),
             ('G2', u'zwischen 10 und 30'),
            ) 


GESPRAECH = (('0', u'Nicht notwendig'),
             ('1', u'Bestanden'),
             ('2', u'Nicht Bestanden'),
            ) 

@provider(IContextSourceBinder)
def un_klasse(context):
    items = []
    for key, value in UN_KLASSE:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


@provider(IContextSourceBinder)
def janein(context):
    items = []
    for key in ('ja', 'nein'):
        items.append(SimpleTerm(key, key, key))
    return SimpleVocabulary(items)


@provider(IContextSourceBinder)
def lieferstopps(context):
    items = []
    for key, value in LIEFERSTOPPS:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


@provider(IContextSourceBinder)
def gespraech(context):
    items = []
    for key, value in GESPRAECH:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


class IKursteilnehmer(Interface):

    id = Int(
        title = u'Id (Kursteilnehmer Id)',
        description = u'Eindeutige Kennzeichnung des Teilnehmers für den Fernlehrgang',
        required = False,
        readonly = True
        )

    teilnehmer_id = TextLine(
        title = u'Id des Teilnehmers',
        description = u'Die Eindeutige Nummer des Teilnehmers',
        required = True,
        )

    fernlehrgang_id = Choice(
        title = u"Lehrgang",
        description = u'Hier können Sie diesen Teilnehmer für einen Lehrgang registrieren.',
        required = False,
        source = named_vocabulary("fernlehrgang"),
        )

    status = Choice(
        title = u"Status",
        description = u"Bitte geben Sie in diesen Feld den Status des Teilnehmers ein",
        required = True,
        default = 'A1',
        source = lieferstopps,
        )

    un_klasse = Choice(
        title = u"Mitarbeiteranzahl",
        description = u'Hier können Sie die Gruppe des Unternehmens festlegen.',
        required = False,
        source = un_klasse,
        )

    branche = Choice(
        title = u"Branche",
        description = u'Betrieb ist ein Recyclingunternehmen, ein Motorradhandel oder ein Speditions- oder Umschalgunternehmen.',
        required = True,
        source = janein,
        default = 'nein',
        )

    gespraech = Choice(
        title = u"Abschlussgesräch / Abschlusseminar",
        description = u'Wie hat der Teilnehmer, falls nötig, das Abschlussgespräch / Abschussseminar absolviert?',
        required = True,
        source = gespraech,
        )
