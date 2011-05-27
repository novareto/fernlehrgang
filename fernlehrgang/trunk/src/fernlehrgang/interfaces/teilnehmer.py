# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grokcore.component as grok
import string

from z3c.saconfig import Session
from random import choice
from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder


# VOCABULARIES

UN_KLASSE = (('G3', u'<= 10'),
             #('G2', u'G III -  = 10, Abschlußgespräch'),
             #('G3', u'G II  - <= 10, Abschlußgespräch'),
             ('G2', u'10 und 30'),
            ) 


@grok.provider(IContextSourceBinder)
def fernlehrgang_vocab(context):
    rc = [SimpleTerm('Keine Registrierung vornehmen', '', '')]
    session = Session()
    from fernlehrgang.models import Fernlehrgang
    for id, titel, jahr in session.query(Fernlehrgang.id, Fernlehrgang.titel, Fernlehrgang.jahr).all():
        value = "%s - %s" % (titel, jahr)
        rc.append(SimpleTerm(id, id, value))
    return SimpleVocabulary(rc)    


@grok.provider(IContextSourceBinder)
def un_klasse(context):
    items = []
    for key, value in UN_KLASSE:
        items.append(SimpleTerm(key, key, value))
    return SimpleVocabulary(items)

@grok.provider(IContextSourceBinder)
def janein(context):
    items = []
    for key in ('ja', 'nein'):
        items.append(SimpleTerm(key, key, key))
    return SimpleVocabulary(items)

def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


# DEFAULTS
def generatePassword():
    pool = string.ascii_letters + string.digits
    return unicode(''.join([choice(pool) for i in range(8)]))


class ITeilnehmer(Interface):

    id = TextLine(
        title = u'Id',
        description = u'Eindeutige Id für den Teilnehmer',
        required = False,
        readonly = True
        )

    anrede = Choice(
        title = u"Anrede",
        description = u'Bitte wählen Sie eine Anrede.',
        required = True,
        vocabulary = vocabulary(
            ('1', 'Herr', 'Herr'),
            ('2', 'Frau', 'Frau'),)
        )

    titel = Choice(
        title = u"Titel",
        description = u'Bitte wählen Sie einen Titel.',
        required = True,
        vocabulary = vocabulary(
            ('0', 'kein Titel', 'kein Titel'),
            ('1', 'Dr.', 'Dr.'),
            ('2', 'Prof.', 'Prof.'),)
        )

    vorname = TextLine(
        title = u'Vorname',
        description = u'Vorname des Teilnehmers',
        required = True
        )

    name = TextLine(
        title = u'Name',
        description = u'Name des Teilnehmers',
        required = True
        )

    geburtsdatum = Date(
        title = u'Geburtsdatum',
        description = u'Geburtsdatum des Teilnehmers',
        required = True
        )

    strasse = TextLine(
        title = u'Lieferanschrift (Str. ',
        description = u'Straße des Teilnehmers',
        required = False, 
        )
    
    nr = TextLine(
        title = u'Hnr.)',
        description = u'Hausnummer des Teilnehmers',
        required = False, 
        )

    plz = TextLine(
        title = u'Lieferanschrift (Plz. ',
        description = u'Postleitzahl des Teilnehmers',
        required = False, 
        )

    ort = TextLine(
        title = u'Ort)',
        description = u'Ort des Teilnehmers',
        required = False, 
        )

    adresszusatz = TextLine(
        title = u'Adresszusatz',
        description = u'Adresszusatz des Teilnehmers',
        required = False 
        )

    email = TextLine(
        title = u'E-Mail',
        description = u'E-Mail des Teilnehmers',
        required = False 
        )

    telefon = TextLine(
        title = u'Telefon',
        description = u'Telefon des Teilnehmers',
        required = False 
        )

    passwort = TextLine(
        title = u'Passwort',
        description = u'Passwort des Teilnehmers',
        required = True,
        defaultFactory = generatePassword,
        )

    lehrgang = Choice(
        title = u"Lehrgang",
        description = u'Hier können Sie diesen Teilnehmer für einen Lehrgang registrieren.',
        required = False,
        source = fernlehrgang_vocab,
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
        )
