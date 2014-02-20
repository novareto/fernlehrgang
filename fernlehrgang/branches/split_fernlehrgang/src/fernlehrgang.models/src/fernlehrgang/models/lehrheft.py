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

from . import Base
from .frage import IFrage, Frage
from .fernlehrgang import Fernlehrgang


@provider(IContextSourceBinder)
def reduce_lehrheft(context):
    from .fernlehrgang import IFernlehrgang
    rc = []
    reduce = []
    alle = range(1, 9)
    if ILehrheft.providedBy(context):
        lehrhefte = context.fernlehrgang.lehrhefte
    if IFernlehrgang.providedBy(context):
        lehrhefte = context.lehrhefte
        reduce = [int(x.nummer) for x in lehrhefte]
    for x in alle:
        if x not in reduce:
            rc.append(SimpleTerm(str(x), str(x), str(x)))
    return SimpleVocabulary(rc)   


class ILehrheft(Interface):

    id = zope.schema.Int(
        title=u'Id',
        description=u'Eindeutige Kennzeichnung des Lehrhefts.',
        required=False,
        readonly=True,
        )

    nummer = zope.schema.Choice(
        title=u'Nummer',
        description=(u'Die Nummer des Lehrhefts. Diese sollte ' +
                     u'fortlaufend 1-8 sein'),
        required=True,
        source=reduce_lehrheft,
        )

    titel = zope.schema.TextLine(
        title=u'Titel',
        description=u'Titel des Lehrhefts.',
        required=True,
        )

    vdatum = zope.schema.Date(
        title=u'Datum der Veröffentlichung',
        description=u'Ab wann soll das Lehrheft veröffentlicht werden.',
        required=True,
        )

    fragen = zope.schema.List(
        title=u"Fragen",
        required=False,
        value_type=zope.schema.Object(schema=IFrage),
        )


@implementer(ILehrheft, IContent)
class Lehrheft(Base):
    __tablename__ = 'lehrheft'

    id = Column(Integer, Sequence('lehrheft_seq', start=1000, increment=1),
                primary_key=True)
    nummer = Column(String(5))
    titel = Column(String(256))
    vdatum = Column(Date())
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))

    fernlehrgang = relation(
        Fernlehrgang, 
        backref=backref(
            'lehrhefte', order_by=nummer.asc(), cascade="all,delete"),
        )

    @property
    def storageid(self):
        return u"%s.%s" % (self.__tablename__, self.id)

    @property
    def title(self):
        return self.titel

    def __repr__(self):
        return "<Lehrgang(id='%s', nummer='%s', fernlehrgangid='%s')>" % (
            self.id, self.nummer, self.fernlehrgang_id)

    @property
    def __content_type__(self):
        return self.__tablename__
    
    fragen = relation(
        Frage,
        order_by=Frage.id,
        backref=backref('lehrheft', cascade="all,delete"),
        )
