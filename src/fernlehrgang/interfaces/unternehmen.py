# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

import grokcore.component as grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder


BETRIEBSARTEN = (
    ("", "Keine Angabe"),
    ("F", "Filiale"),
    ("E", "Einzelbetrieb"),
    ("Z", "Zentrale"),
    ("H", "Hauptbetrieb"),
    ("B", "Betriebsteil"),
)


@grok.provider(IContextSourceBinder)
def voc_betriebsart(context):
    items = []
    for key, value in BETRIEBSARTEN:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


class IUnternehmen(Interface):
    mnr = TextLine(
        title="Mitgliedsnummer",
        description="Mitgliedsnummer des Unternehmens",
        required=False,
        readonly=False,
    )

    unternehmensnummer = TextLine(
        title="Unternehmensnummer",
        description="Unternehmensnummer des Unternehmens",
        required=False,
        readonly=False,
    )

    name = TextLine(title="Name", description="Name des Unternehmens", required=True)

    name2 = TextLine(title="Name2", description="Name des Unternehmens", required=True)

    name3 = TextLine(title="Name3", description="Name des Unternehmens", required=True)

    str = TextLine(
        title="Strasse", description="Strasse des Unternehmens", required=True
    )

    plz = TextLine(
        title="Postleitzahl", description="Postleitzahl des Unternehmens", required=True
    )

    ort = TextLine(title="Ort", description="Ort des Unternehmens", required=True)

    betriebsart = Choice(
        title="Betriebsart",
        description="Betriebsart des Unternehmens",
        source=voc_betriebsart,
        required=True,
    )

    mnr_g_alt = TextLine(
        title="Mitgliedsnummer G Alt",
        description="Alte Mitgliedsnummern der Sparte G",
        required=False,
    )

    b_groesse = TextLine(
        title="Betriebsgröße",
        description="Betriebsgröße (Zahlen von CUSA)",
        required=False,
    )

    hbst = TextLine(
        title="Hauptbetriebsstätte",
        description="Hauptbetriebsstätte (ID der Hauptbetriebsstätte)",
        required=False,
    )
