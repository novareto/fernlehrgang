# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import string
from random import choice

from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy_imageattach.context import get_current_store
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.entity import store_context

import zope.schema
from zope.interface import Interface
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from . import Base, MyStringType
from .unternehmen import Unternehmen
from zope.location.interfaces import ILocation


# VOCABULARIES
def vocabulary(*terms):
    return SimpleVocabulary(
        [SimpleTerm(value, token, title) for value, token, title in terms])


# DEFAULTS
def generatePassword():
    pool = string.ascii_letters + string.digits
    for c in ['o', 'O', '0', 'l', 'I', 'q', 'g']:
        pool = pool.replace(c, '')
    return unicode(''.join([choice(pool) for i in range(8)]))


class ITeilnehmer(Interface):

    id = zope.schema.TextLine(
        title = u'Id',
        description = u'Eindeutige Id für den Teilnehmer',
        required = False,
        readonly = True
        )

    anrede = zope.schema.Choice(
        title = u"Anrede",
        description = u'Bitte wählen Sie eine Anrede.',
        required = True,
        vocabulary = vocabulary(
            ('1', 'Herr', 'Herr'),
            ('2', 'Frau', 'Frau'),)
        )

    titel = zope.schema.Choice(
        title = u"Titel",
        description = u'Bitte wählen Sie einen Titel.',
        required = True,
        vocabulary = vocabulary(
            ('0', 'kein Titel', 'kein Titel'),
            ('1', 'Dr.', 'Dr.'),
            ('2', 'Prof.', 'Prof.'),)
        )

    vorname = zope.schema.TextLine(
        title = u'Vorname',
        description = u'Vorname des Teilnehmers',
        required = True
        )

    name = zope.schema.TextLine(
        title = u'Name',
        description = u'Name des Teilnehmers',
        required = True
        )

    geburtsdatum = zope.schema.Date(
        title = u'Geburtsdatum',
        description = u'Geburtsdatum des Teilnehmers',
        required = True
        )

    strasse = zope.schema.TextLine(
        title = u'Lieferanschrift (Str. ',
        description = u'Straße des Teilnehmers',
        required = False, 
        )
    
    nr = zope.schema.TextLine(
        title = u'Hnr.)',
        description = u'Hausnummer des Teilnehmers',
        required = False, 
        )

    plz = zope.schema.TextLine(
        title = u'Lieferanschrift (Plz. ',
        description = u'Postleitzahl des Teilnehmers',
        required = False, 
        )

    ort = zope.schema.TextLine(
        title = u'Ort)',
        description = u'Ort des Teilnehmers',
        required = False, 
        )

    adresszusatz = zope.schema.TextLine(
        title = u'Adresszusatz',
        description = u'Adresszusatz des Teilnehmers',
        required = False 
        )

    email = zope.schema.TextLine(
        title = u'E-Mail',
        description = u'E-Mail des Teilnehmers',
        required = False 
        )

    telefon = zope.schema.TextLine(
        title = u'Telefon',
        description = u'Telefon des Teilnehmers',
        required = False 
        )

    passwort = zope.schema.TextLine(
        title = u'Passwort',
        description = u'Passwort des Teilnehmers',
        required = True,
        defaultFactory = generatePassword,
        )

    kategorie = zope.schema.Choice(
        title = u"Kategorie",
        description = u'Bitte wählen Sie eine Kategorie.',
        required = True,
        default = '0',
        vocabulary = vocabulary(
            ('0', '0', 'Keine Kategorie'),
            ('1', 'K1', 'Kategorie 1'),
            ('2', 'K2', 'Kategorie 2'),)
        )

    kompetenzzentrum = zope.schema.Choice(
        title = u"Kompetenzzentrum",
        description = u'Datenfreigabe erteilt?',
        required = True,
        default = 'nein',
        vocabulary = vocabulary(
            ('nein', 'nein', 'Nein'),
            ('ja', 'ja', 'Ja'),
            )
        )


@implementer(ITeilnehmer, ILocation)
class Teilnehmer(Base):
    __tablename__ = 'teilnehmer'

    id = Column(Integer,
                Sequence('teilnehmer_seq', start=100000, increment=1),
                primary_key=True)

    anrede = Column(String(50))
    titel = Column(String(50))
    vorname = Column(String(50))
    name = Column(MyStringType(50))
    geburtsdatum = Column(Date)
    strasse = Column(String(50))
    nr = Column(String(50))
    plz = Column(String(50))
    ort = Column(String(50))
    adresszusatz = Column(String(50))
    email = Column(String(50))
    telefon = Column(String(50))
    passwort = Column(String(8))
    kategorie = Column(String(1))
    kompetenzzentrum = Column(String(5))

    unternehmen_mnr = Column(String(12), ForeignKey('adr.MNR'))

    unternehmen = relation(Unternehmen,
                           backref = backref('teilnehmer', order_by=id))

    @property
    def title(self):
        return "%s %s" % (self.name, self.vorname)

    password = passwort

    def __repr__(self):
        return "<Teilnehmer(id='%s', name='%s')>" % (self.id, self.name)
