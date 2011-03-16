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


@grok.provider(IContextSourceBinder)
def fernlehrgang_vocab(context):
    rc = []
    session = Session()
    from fernlehrgang.models import Fernlehrgang
    for id, titel, jahr in session.query(Fernlehrgang.id, Fernlehrgang.titel, Fernlehrgang.jahr).all():
        value = "%s - %s" % (titel, jahr)
        rc.append(SimpleTerm(id, id, value))
    return SimpleVocabulary(rc)    


def generatePassword():
    pool = string.ascii_letters + string.digits
    return ''.join([choice(pool) for i in range(8)])


def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


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
        title = u'Straße',
        description = u'Straße des Teilnehmers',
        required = False, 
        )
    
    nr = TextLine(
        title = u'Hausnummer',
        description = u'Hausnummer des Teilnehmers',
        required = False, 
        )

    plz = TextLine(
        title = u'Postleitzahl',
        description = u'Postleitzahl des Teilnehmers',
        required = False, 
        )

    ort = TextLine(
        title = u'Ort',
        description = u'Ort des Teilnehmers',
        required = False, 
        )

    email = TextLine(
        title = u'E-Mail',
        description = u'E-Mail des Teilnehmers',
        required = True
        )

    passwort = TextLine(
        title = u'Passwort',
        description = u'Passwort des Teilnehmers',
        required = True,
        )

    lehrgang = Choice(
        title = u"Lehrgang",
        description = u'Hier können Sie diesen Teilnehmer für einen Lehrgang registrieren.',
        required = False,
        source = fernlehrgang_vocab,
        )
