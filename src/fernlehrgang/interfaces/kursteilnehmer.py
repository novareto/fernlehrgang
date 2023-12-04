# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

import grokcore.component as grok
import datetime

from z3c.saconfig import Session
from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder
from fernlehrgang.interfaces.app import IFernlehrgangApp


def today():
    return datetime.date.today()


LIEFERSTOPPS = (
    ("L1", "UN-Modell anderer UV-Träger"),
    ("L2", "Grund- bzw. Regelbetreuung"),
    ("L3", "keine Beschäftigten"),
    ("L4", "Teilnahme aus pers. Gründen verschoben"),
    ("L5", "Teilnahme ist bereits erfolgt"),
    ("L6", "Aufgabe des Unternehmens"),
    ("L7", "TN nicht mehr im Unternehmen"),
    ("L8", "UN nicht aktiv im Betriebsgeschehen"),
    ("L9", "TN kein Unternehmer"),
    ("S1", "Interner Fehler"),
    ("A1", "angemeldet"),
    ("A2", "nicht registriert"),
    ("Z1", "Bearbeitungsfrist abgelaufen"),
)


UN_KLASSE = (
    ("G3", "<= 10"),
    ("G2", "zwischen 10 und 30"),
    #             ('G', u'zwischen 30 und 50'),
    ("G1", "zwischen 30 und 50"),  # Achtung Neue Gruppe muss wieder raus
)


GESPRAECH = (
    ("0", "Nicht notwendig"),
    ("1", "Bestanden"),
    ("2", "Nicht Bestanden"),
)


@grok.provider(IContextSourceBinder)
def un_klasse(context):
    items = []
    for key, value in UN_KLASSE:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


@grok.provider(IContextSourceBinder)
def janein(context):
    items = []
    for key in ("ja", "nein"):
        items.append(SimpleTerm(key, key, key))
    return SimpleVocabulary(items)


@grok.provider(IContextSourceBinder)
def lieferstopps(context):
    items = []
    for key, value in LIEFERSTOPPS:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


@grok.provider(IContextSourceBinder)
def gespraech(context):
    items = []
    for key, value in GESPRAECH:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)


@grok.provider(IContextSourceBinder)
def fernlehrgang_vocab(context):
    rc = [SimpleTerm("", "", "Fernlehrgang auswählen")]
    session = Session()
    from fernlehrgang.models import Fernlehrgang

    sql = session.query(Fernlehrgang).order_by(Fernlehrgang.id.desc())

    def getKTN(context, flg_id):
        if IFernlehrgangApp.providedBy(context):
            return
        if not hasattr(context, "kursteilnehmer"):
            return True
        for x in context.kursteilnehmer:
            if flg_id == x.fernlehrgang_id:
                return x

    for flg in sql.all():
        ktn = getKTN(context, flg.id)
        if ktn:
            value = "%s - %s, bereits Registriert" % (flg.titel, flg.jahr)
            if ktn is True:
                token = flg.id
            else:
                token = "%s,%s" % (ktn.id, flg.id)
            rc.append(SimpleTerm(token, token, value))
        else:
            value = "%s - %s" % (flg.titel, flg.jahr)
            rc.append(SimpleTerm(flg.id, flg.id, value))
    return SimpleVocabulary(rc)


class IKursteilnehmer(Interface):
    id = Int(
        title="Id (Kursteilnehmer Id)",
        description="Eindeutige Kennzeichnung des Teilnehmers für den Fernlehrgang",
        required=False,
        readonly=True,
    )

    teilnehmer_id = Int(
        title="Id des Teilnehmers",
        description="Die Eindeutige Nummer des Teilnehmers",
        required=True,
    )

    fernlehrgang_id = Choice(
        title="Lehrgang",
        description=(
            "Hier können Sie diesen Teilnehmer für einen Lehrgang registrieren."
        ),
        required=False,
        source=fernlehrgang_vocab,
    )

    status = Choice(
        title="Status",
        description="Bitte geben Sie in diesen Feld den Status des Teilnehmers ein",
        required=True,
        default="A1",
        source=lieferstopps,
    )

    erstell_datum = Date(
        title="Erstelldatum",
        description="Datum der Erstellung des Kursteilnehmers",
        required=False,
        defaultFactory=today,
        # readonly = True,
    )

    un_klasse = Choice(
        title="Mitarbeiteranzahl",
        description="Hier können Sie die Gruppe des Unternehmens festlegen.",
        required=False,
        source=un_klasse,
    )

    branche = Choice(
        title="Branche",
        description=(
            "Betrieb ist ein Recyclingunternehmen, ein Motorradhandel oder ein"
            " Speditions- oder Umschalgunternehmen."
        ),
        required=True,
        source=janein,
        default="nein",
    )

    gespraech = Choice(
        title="Abschlussgespräch / Abschlusseminar",
        description=(
            "Wie hat der Teilnehmer, falls nötig, das Abschlussgespräch /"
            " Abschussseminar absolviert?"
        ),
        required=True,
        source=gespraech,
    )


class IVLWKursteilnehmer(IKursteilnehmer):
    """Marker Interface for Kursteilnehmer regsitered on VLW's"""


class IFortbildungKursteilnehmer(IKursteilnehmer):
    """Marker Interface for Kursteilnehmer regsitered on Fortbildung"""
