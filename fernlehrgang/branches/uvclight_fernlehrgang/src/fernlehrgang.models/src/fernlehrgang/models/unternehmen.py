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

from . import Base, MyStringType


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

    mnr = zope.schema.TextLine(
        title = u'Mitgliedsnummer',
        description = u'Mitgliedsnummer des Unternehmens',
        required = False,
        readonly = False, 
        )

    name = zope.schema.TextLine(
        title = u'Name',
        description = u'Name des Unternehmens',
        required = True
        )

    name2 = zope.schema.TextLine(
        title = u'Name2',
        description = u'Name des Unternehmens',
        required = True
        )

    name3 = zope.schema.TextLine(
        title = u'Name3',
        description = u'Name des Unternehmens',
        required = True
        )

    str = zope.schema.TextLine(
        title = u'Strasse',
        description = u'Strasse des Unternehmens',
        required = True
        )

    plz = zope.schema.TextLine(
        title = u'Postleitzahl',
        description = u'Postleitzahl des Unternehmens',
        required = True
        )

    ort = zope.schema.TextLine(
        title = u'Ort',
        description = u'Ort des Unternehmens',
        required = True
        )

    betriebsart = zope.schema.Choice(
        title = u'Betriebsart',
        description = u'Betriebsart des Unternehmens',
        source = voc_betriebsart,
        required = True
        )

    mnr_g_alt = zope.schema.TextLine(
        title = u'Mitgliedsnummer G Alt',
        description = u'Alte Mitgliedsnummern der Sparte G',
        required = False, 
        )


@implementer(IUnternehmen, IContent, ILocation)
class Unternehmen(Base):
    __tablename__ = 'adr'

    #id = Column("ID", Numeric, primary_key=True)
    mnr = Column("MNR", MyStringType(12), primary_key=True, index=True)
    name = Column("NAME1", String(32))
    name2 = Column("NAME2", String(32))
    name3 = Column("NAME3", String(32))
    str = Column("STR", String(70))
    plz = Column("PLZ", String(10))
    ort = Column("ORT", String(30))
    betriebsart = Column("BETRIEBSART", String(1))
    mnr_e = Column("MNR_E", MyStringType(12))
    mnr_g_alt = Column("MNR_G_ALT", MyStringType(12))

    @property
    def title(self):
        return self.mnr

    def __repr__(self):
        return "<Unternehmen(mnr='%s')>" %(self.mnr)

    @property
    def __content_type__(self):
        return self.__tablename__
