# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 


import grok

from megrok import traject

from sqlalchemy import *
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

from z3c.saconfig import Session
from z3c.saconfig.interfaces import IEngineCreatedEvent

from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang
from fernlehrgang.interfaces.frage import IFrage
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer

from zope.container.contained import Contained

@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    metadata = Base.metadata
    metadata.create_all(event.engine)


Base = declarative_base()


class RDBMixin(traject.Model, Contained):
    """ Base Mixin for RDB-Base Classes """
    grok.baseclass()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Fernlehrgang(Base, RDBMixin):
    grok.implements(IFernlehrgang)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id")

    __tablename__ = 'fernlehrgang'

    id = Column(Integer, primary_key=True)
    jahr = Column(Integer)
    titel = Column(String)
    beschreibung = Column(String)
    start = Column(Date)
    ende = Column(Date)


    def __repr__(self):
        return "<Fernlehrgang(id='%s', jahr='%s', titel='%s')>" %(self.id, self.jahr, self.titel)

    def factory(fernlehrgang_id):
        session = Session()
        return session.query(Fernlehrgang).filter(
            Fernlehrgang.id == int(fernlehrgang_id)).one()

    def arguments(fernlehrgang):
        return dict(fernlehrgang_id = fernlehrgang.id)


class Unternehmen(Base, RDBMixin):
    grok.implements(IUnternehmen)
    grok.context(IFernlehrgangApp)
    traject.pattern("unternehmen/:mnr")

    __tablename__ = 'unternehmen'

    mnr = Column(String, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<Unternehmen(mnr='%s')>" %(self.mnr)

    def factory(mnr):
        session = Session()
        return session.query(Unternehmen).filter(
            Unternehmen.id == mnr).one()

    def arguments(unternehmen):
        return dict(mnr = unternehmen.mnr)


class Teilnehmer(Base, RDBMixin):
    grok.implements(ITeilnehmer)
    grok.context(IFernlehrgangApp)
    traject.pattern("teilnehmer/:id")

    __tablename__ = 'teilnehmer'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<Teilnehmer(id='%s', name='%s')>" %(self.id, self.name)

    def factory(id):
        session = Session()
        return session.query(Teilnehmer).filter(
            Teilnehmer.id == id).one()

    def arguments(teilnehmer):
        return dict(id = teilnehmer.id)


class Lehrheft(Base, RDBMixin):
    grok.implements(ILehrheft)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id")

    __tablename__ = 'lehrheft'

    id = Column(Integer, primary_key=True)
    nummer = Column(Integer)
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))

    fernlehrgang = relation(Fernlehrgang, backref = backref('lehrhefte', order_by=nummer))

    def __repr__(self):
        return "<Lehrgang(id='%s', nummer='%s', fernlehrgangid='%s')>" %(self.id, self.nummer, self.fernlehrgang_id)

    def factory(fernlehrgang_id, lehrheft_id):
        session = Session()
        return  session.query(Lehrheft).filter(
            and_( Lehrheft.fernlehrgang_id == int(fernlehrgang_id),
                  Lehrheft.id == int(lehrheft_id))).one()

    def arguments(lehrheft):
        return dict(fernlehrgang_id = lehrheft.fernlehrgang_id,
                    lehrheft_id = lehrheft.id)



class Frage(Base, RDBMixin):
    grok.implements(IFrage)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id/resultat/:resultat_id")

    __tablename__ = 'resultat'

    id = Column(Integer, primary_key=True)
    frage = Column(Integer)
    antwortschema = Column(String)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id',))

    lehrheft = relation(Lehrheft, backref = backref('fragen', order_by=frage))

    def __repr__(self):
        return "<Frage(id='%s', frage='%s', antwort='%s')>" %(self.id, self.frage, self.antwortschema)

    def factory(fernlehrgang_id, lehrheft_id, resultat_id):
        session = Session()
        return  session.query(Frage).filter(
            and_( Frage.id == int(resultat_id),
                  Frage.lehrheft_id == int(lehrheft_id))).one()

    def arguments(resultat):
        return dict(resultat_id = resultat.id,
                    lehrheft_id = resultat.lehrheft_id,
                    fernlehrgang_id = resultat.lehrheft.fernlehrgang.id)


class Kursteilnehmer(Base, RDBMixin):
    grok.implements(IKursteilnehmer)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/kursteilnehmer/:kursteilnehmer_id")

    __tablename__ = 'kursteilnehmer'

    id = Column(Integer, primary_key=True)
    status = Column(String)
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id',))
    unternehmen_mnr = Column(String, ForeignKey('unternehmen.mnr',))

    fernlehrgang = relation(Fernlehrgang, backref = backref('kursteilnehmer', order_by=id))

    def __repr__(self):
        return "<Kursteilnehmer(id='%s', fernlehrgangid='%s')>" %(self.id, self.fernlehrgang_id)

    def factory(fernlehrgang_id, id):
        session = Session()
        return  session.query(Kursteilnehmer).filter(
            and_( Kursteilnehmer.fernlehrgang_id == int(fernlehrgang_id),
                  Kursteilnehmer.id == int(id))).one()

    def arguments(kursteilnehmer):
        return dict(fernlehrgang_id = kursteilnehmer.fernlehrgang_id,
                    id = kursteilnehmer.id)

