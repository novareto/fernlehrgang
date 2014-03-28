# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

from dolmen.content import IContent
from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy_imageattach.context import get_current_store
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.entity import store_context

import zope.schema
from zope.interface import Interface, provider
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.location import ILocation

from . import Base
from .fernlehrgang import Fernlehrgang
from .teilnehmer import Teilnehmer
from .unternehmen import Unternehmen
from .vocabularies import named_vocabulary



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

    id = zope.schema.Int(
        title = u'Id (Kursteilnehmer Id)',
        description = (u'Eindeutige Kennzeichnung des Teilnehmers '
                       u'für den Fernlehrgang'),
        required = False,
        readonly = True
        )

    teilnehmer_id = zope.schema.TextLine(
        title = u'Id des Teilnehmers',
        description = u'Die Eindeutige Nummer des Teilnehmers',
        required = True,
        )

    fernlehrgang_id = zope.schema.Choice(
        title = u"Lehrgang",
        description = (u'Hier können Sie diesen Teilnehmer für '
                       u'einen Lehrgang registrieren.'),
        required = False,
        source = named_vocabulary("fernlehrgang"),
        )

    status = zope.schema.Choice(
        title = u"Status",
        description = (u"Bitte geben Sie in diesen Feld den Status "
                       u"des Teilnehmers ein"),
        required = True,
        default = 'A1',
        source = lieferstopps,
        )

    un_klasse = zope.schema.Choice(
        title = u"Mitarbeiteranzahl",
        description = (u"Hier können Sie die Gruppe des Unternehmens "
                       u"festlegen."),
        required = False,
        source = un_klasse,
        )

    branche = zope.schema.Choice(
        title = u"Branche",
        description = (u'Betrieb ist ein Recyclingunternehmen, ein '
                       u'Motorradhandel oder ein Speditions- oder '
                       u'Umschalgunternehmen.'),
        required = True,
        source = janein,
        default = 'nein',
        )

    gespraech = zope.schema.Choice(
        title = u"Abschlussgesräch / Abschlusseminar",
        description = (u'Wie hat der Teilnehmer, falls nötig, das '
                       u'Abschlussgespräch / Abschussseminar absolviert ?'),
        required = True,
        source = gespraech,
        )


@implementer(IKursteilnehmer, IContent, ILocation)
class Kursteilnehmer(Base):
    __tablename__ = 'kursteilnehmer'

    id = Column(
        Integer,
        Sequence('kursteilnehmer_seq', start=900000, increment=1),
        primary_key=True)

    status = Column(String(50))
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id',))
    unternehmen_mnr = Column(String(12), ForeignKey('adr.MNR',))
    un_klasse = Column(String(3))
    branche = Column(String(5))
    gespraech = Column(String(20))

    fernlehrgang = relation(
        Fernlehrgang,
        backref=backref('kursteilnehmer', order_by=id))

    teilnehmer = relation(
        Teilnehmer,
        backref=backref('kursteilnehmer', order_by=id))
    
    unternehmen = relation(
        Unternehmen,
        backref=backref('kursteilnehmer', order_by=id))

    @property
    def title(self):
        return "%s %s" % (self.teilnehmer.name, self.teilnehmer.vorname)

    @property
    def __content_type__(self):
        return self.__tablename__

    def __repr__(self):
        return "<Kursteilnehmer(id='%s', fernlehrgangid='%s')>" % (
            self.id, self.fernlehrgang_id)
