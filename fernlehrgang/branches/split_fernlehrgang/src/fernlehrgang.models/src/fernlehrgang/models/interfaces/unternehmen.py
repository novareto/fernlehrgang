# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

from zope.schema import *
from zope.interface import Interface, provider
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder


BETRIEBSARTEN = (
        ('', u'Keine Angabe'),
        ('F', u'Filiale'),
        ('E', u'Einzelbetrieb'),
        ('Z', u'Zentrale'),
        ('H', u'Hauptbetrieb'),
        ('B', u'Betriebsteil')
        )


@provider(IContextSourceBinder)
def voc_betriebsart(context):
    items = []
    for key, value in BETRIEBSARTEN:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


class IUnternehmen(Interface):

    mnr = TextLine(
        title = u'Mitgliedsnummer',
        description = u'Mitgliedsnummer des Unternehmens',
        required = False,
        readonly = False, 
        )

    name = TextLine(
        title = u'Name',
        description = u'Name des Unternehmens',
        required = True
        )

    name2 = TextLine(
        title = u'Name2',
        description = u'Name des Unternehmens',
        required = True
        )

    name3 = TextLine(
        title = u'Name3',
        description = u'Name des Unternehmens',
        required = True
        )

    str = TextLine(
        title = u'Strasse',
        description = u'Strasse des Unternehmens',
        required = True
        )

    plz = TextLine(
        title = u'Postleitzahl',
        description = u'Postleitzahl des Unternehmens',
        required = True
        )

    ort = TextLine(
        title = u'Ort',
        description = u'Ort des Unternehmens',
        required = True
        )

    betriebsart = Choice(
        title = u'Betriebsart',
        description = u'Betriebsart des Unternehmens',
        source = voc_betriebsart,
        required = True
        )

    mnr_g_alt = TextLine(
        title = u'Mitgliedsnummer G Alt',
        description = u'Alte Mitgliedsnummern der Sparte G',
        required = False, 
        )
