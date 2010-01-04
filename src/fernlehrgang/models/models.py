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
from fernlehrgang.interfaces.resultat import IResultat

from zope.container.contained import Contained

@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    metadata = Base.metadata
    metadata.create_all(event.engine)


Base = declarative_base()

class Fernlehrgang(Base, traject.Model, Contained):
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

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Fernlehrgang(id='%s', jahr='%s', titel='%s')>" %(self.id, self.jahr, self.titel)

    def factory(fernlehrgang_id):
        session = Session()
        return session.query(Fernlehrgang).filter(
            Fernlehrgang.id == int(fernlehrgang_id)).one()

    def arguments(fernlehrgang):
        return dict(fernlehrgang_id = fernlehrgang.id)



class Lehrheft(Base, traject.Model, Contained):
    grok.implements(ILehrheft)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id")

    __tablename__ = 'lehrheft'

    id = Column(Integer, primary_key=True)
    nummer = Column(Integer)
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))

    fernlehrgang = relation(Fernlehrgang, backref = backref('lehrhefte', order_by=nummer))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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



class Resultat(Base, traject.Model, Contained):
    grok.implements(IResultat)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id/resultat/:resultat_id")

    __tablename__ = 'resultat'

    id = Column(Integer, primary_key=True)
    frage = Column(Integer)
    antwortschema = Column(String)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id',))

    lehrheft = relation(Lehrheft, backref = backref('resultate', order_by=frage))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Resultat(id='%s', frage='%s', antwort='%s')>" %(self.id, self.frage, self.antwortschema)

    def factory(fernlehrgang_id, lehrheft_id, resultat_id):
        session = Session()
        return  session.query(Resultat).filter(
            and_( Resultat.id == int(resultat_id),
                  Resultat.lehrheft_id == int(lehrheft_id))).one()

    def arguments(resultat):
        return dict(resultat_id = resultat.id,
                    lehrheft_id = resultat.lehrheft_id,
                    fernlehrgang_id = resultat.lehrheft.fernlehrgang.id)
