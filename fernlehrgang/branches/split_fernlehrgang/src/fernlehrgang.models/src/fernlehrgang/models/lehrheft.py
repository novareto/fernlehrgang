# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy_imageattach.context import get_current_store
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.entity import store_context
from zope.interface import Interface, provider
from zope.interface import implementer
from zope.schema import *
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from .frage import IFrage


@provider(IContextSourceBinder)
def reduce_lehrheft(context):
    from fernlehrgang.interfaces.flg import IFernlehrgang
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

    id = Int(
        title=u'Id',
        description=u'Eindeutige Kennzeichnung des Lehrhefts.',
        required=False,
        readonly=True,
        )

    nummer = Choice(
        title=u'Nummer',
        description=(u'Die Nummer des Lehrhefts. Diese sollte ' +
                     u'fortlaufend 1-8 sein'),
        required=True,
        source=reduce_lehrheft,
        )

    titel = TextLine(
        title=u'Titel',
        description=u'Titel des Lehrhefts.',
        required=True,
        )

    vdatum = Date(
        title=u'Datum der Veröffentlichung',
        description=u'Ab wann soll das Lehrheft veröffentlicht werden.',
        required=True,
        )

    fragen = List(
        title=u"Fragen",
        required=False,
        value_type=Object(schema=IFrage),
        )


@implementer(ILehrheft)
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
