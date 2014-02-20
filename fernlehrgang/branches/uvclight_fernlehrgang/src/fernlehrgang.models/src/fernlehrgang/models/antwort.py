# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

from datetime import datetime
from dolmen.content import IContent
from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy_imageattach.context import get_current_store
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.entity import store_context
from zope.interface import Interface
from zope.interface import implementer
from zope.schema import *
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from . import Base
from .vocabularies import named_vocabulary
from .kursteilnehmer import IKursteilnehmer, Kursteilnehmer
from .frage import IFrage, Frage


def vocabulary(*terms):
    return SimpleVocabulary(
        [SimpleTerm(value, token, title) for value, token, title in terms])


class IAntwort(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung der Antwort',
        required = False,
        readonly = True
        )

    lehrheft_id = Choice(
        title = u'Lehrheft',
        description = u'Für welches Lehrheft liegt eine Antwort vor.',
        required = True,
        source = named_vocabulary('lehrheft'),
        )

    frage_id = Choice(
        title = u'Frage',
        description = u'Für welche Frage soll das Antwortschema sein.',
        required = True,
        source = named_vocabulary('fragen'),
        )

    antwortschema = TextLine(
        title = u'Antwortschema',
        description = u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required = True,
        default = u'',
        )

    datum = Datetime(
        title = u'Datum',
        description = u'Modifikationsdatum',
        required = False,
        readonly = False,
        defaultFactory = datetime.now,
        default = datetime.now(),
        )

    system = Choice(
        title = u'Eingabesystem',
        description = (u'Bitte geben Sie an wie diese Antwort ins ' +
                       u'System gekommen ist.'),
        required = True,
        vocabulary=vocabulary(
            ('FernlehrgangApp', 'FernlehrgangApp', 'FernlehrgangApp'),
            ('Extranet', 'Extranet', 'Extranet'),
            ),
        )


@implementer(IAntwort, IContent)
class Antwort(Base):
    __tablename__ = 'antwort'
    __table_args__ = (
        UniqueConstraint('frage_id', 'kursteilnehmer_id', name="unique_frage"),
        {})

    id = Column(Integer,
                Sequence('antwort_seq', start=100000, increment=1),
                primary_key=True)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id'))
    frage_id = Column(Integer, ForeignKey('frage.id'))
    antwortschema = Column(String(50))
    datum = Column(DateTime)
    system = Column(String(50))
    kursteilnehmer_id = Column(Integer, ForeignKey('kursteilnehmer.id',))

    kursteilnehmer = relation(
        Kursteilnehmer, 
        backref=backref('antworten', order_by=frage_id, cascade="all,delete"),
        )

    frage = relation(Frage)
                     
    @property
    def title(self):
        return self.frage.titel

    @property
    def __content_type__(self):
        return self.__tablename__
    
    def __repr__(self):
        return "<Antwort(id='%s', frage='%s', antwort='%s')>" % (
            self.id, self.frage_id, self.antwortschema)
