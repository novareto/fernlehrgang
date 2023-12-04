# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

import grokcore.component as grok

from zope.schema import *
from zope.interface import Interface

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder


@grok.provider(IContextSourceBinder)
def jahre(context):
    items = []
    for jahr in range(2011, 2025, 1):
        jahr = str(jahr)
        items.append(SimpleTerm(jahr, jahr, jahr))
    return SimpleVocabulary(items)


@grok.provider(IContextSourceBinder)
def typ(context):
    return SimpleVocabulary(
        (
            SimpleTerm("1", "1", "Fernlehrgang"),
            SimpleTerm("2", "2", "Online Fernlehrgang"),
            SimpleTerm("3", "3", "Fortbildung"),
            SimpleTerm("4", "4", "Virtuelle Lernwelt"),
            SimpleTerm("5", "5", "Online Fortbildung"),
        )
    )


class IFernlehrgang(Interface):
    id = Int(
        title="Id",
        description="Eindeutige Kennzeichnung des Fernlehrgangs",
        required=False,
        readonly=True,
    )

    jahr = Choice(
        title="Jahr",
        description="Das Jahr in dem der Fernlehrgang stattfindent",
        required=True,
        source=jahre,
    )

    titel = TextLine(
        title="Titel", description="Titel des Fernlehrgangs", required=True
    )

    beschreibung = Text(
        title="Beschreibung",
        description="Beschreibung des Fernlehrgangs",
        required=True,
    )

    typ = Choice(
        title="Typ des Fernlehrgang",
        description="Bitte wählen Sie den Typ des Fernlehrgangs aus",
        source=typ,
        required=True,
    )

    punktzahl = Int(
        title="Punkteanzahl",
        description=(
            "Bitte geben Sie hier die Punkteanzahl an, die "
            "erreicht werden muss, um den Fernlehrgang zu bestehen"
        ),
        required=True,
    )

    beginn = Date(
        title="Start",
        description="Zu welchem Datum soll der Fernlehrgang beginnen?",
        required=True,
    )

    ende = Date(
        title="Ende",
        description="Zu welchem Datum soll der Fernlehrgang enden?",
        required=True,
    )

    id_mapping = Int(
        title="VLW-ID-Mapping",
        description=(
            "Bitte geben Sie hier eine alternative ID an, die "
            "der Teilnehmer an die VLW idnetifiziert."
        ),
    )
