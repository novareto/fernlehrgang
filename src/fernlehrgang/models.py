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
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.frage import IFrage
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.antwort import IAntwort

from zope.container.contained import Contained

Base = declarative_base()
Base1 = declarative_base()

@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    metadata = Base.metadata
    metadata.create_all(event.engine, checkfirst=True)



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

    id = Column(Integer, Sequence('fernlehrgang_id'), primary_key=True)
    jahr = Column(Integer)
    titel = Column(String(50))
    beschreibung = Column(String(50))
    punktzahl = Column(Integer(4))
    beginn = Column(Date)
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
    traject.pattern("unternehmen/:unternehmen_id")

    __tablename__ = 'adr'

    id = Column("ID", Numeric, primary_key=True)
    mnr = Column("MNR", String(12))
    typ = Column("TYP", String(3))
    name = Column("NAME1", String(32))
    name2 = Column("NAME2", String(32))
    name3 = Column("NAME3", String(32))
    str = Column("STR", String(70))
    plz = Column("PLZ", String(10))
    ort = Column("ORT", String(30))
    plz = Column("PLZ", String(10))

    def __repr__(self):
        return "<Unternehmen(mnr='%s')>" %(self.mnr)

    def factory(unternehmen_id):
        session = Session()
        return session.query(Unternehmen).filter(
            Unternehmen.id == unternehmen_id).one()

    def arguments(unternehmen):
        return dict(unternehmen_id = unternehmen.id)


class Teilnehmer(Base, RDBMixin):
    grok.implements(ITeilnehmer)
    grok.context(IFernlehrgangApp)
    traject.pattern("unternehmen/:unternehmen_id/teilnehmer/:id")

    __tablename__ = 'teilnehmer'

    id = Column(Integer, Sequence('teilnehmer_seq'), primary_key=True)

    anrede = Column(String(50))
    titel = Column(String(50))
    vorname = Column(String(50))
    name = Column(String(50))
    geburtsdatum = Column(Date)
    strasse = Column(String(50))
    nr = Column(String(50))
    plz = Column(String(50))
    ort = Column(String(50))
    email = Column(String(50))

    unternehmen_id = Column(Numeric, ForeignKey('adr.ID'))

    unternehmen = relation(Unternehmen,
                           backref = backref('teilnehmer', order_by=id))

    def __repr__(self):
        return "<Teilnehmer(id='%s', name='%s')>" %(self.id, self.name)

    def factory(id, unternehmen_id):
        session = Session()
        return session.query(Teilnehmer).filter(
            and_(Teilnehmer.id == id, Teilnehmer.unternehmen_id == unternehmen_id)).one()

    def arguments(teilnehmer):
        return dict(id = teilnehmer.id, unternehmen_id = teilnehmer.unternehmen_id)


class Lehrheft(Base, RDBMixin):
    grok.implements(ILehrheft)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id")

    __tablename__ = 'lehrheft'

    id = Column(Integer, Sequence('lehrheft_seq'), primary_key=True)
    nummer = Column(Integer)
    titel = Column(String(50))
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))

    fernlehrgang = relation(Fernlehrgang, 
                            backref = backref('lehrhefte', order_by=nummer),
                           ) 

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
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id/frage/:frage_id")

    __tablename__ = 'frage'

    id = Column(Integer, Sequence('frage_id'), primary_key=True)
    frage = Column(Integer)
    titel = Column(String(50))
    antwortschema = Column(String(50))
    gewichtung = Column(Integer)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id',))

    lehrheft = relation(Lehrheft, 
                        backref = backref('fragen', order_by=frage),
                        )

    def __repr__(self):
        return "<Frage(id='%s', frage='%s', antwort='%s')>" %(self.id, self.frage, self.antwortschema)

    def factory(fernlehrgang_id, lehrheft_id, frage_id):
        session = Session()
        return  session.query(Frage).filter(
            and_( Frage.id == int(frage_id),
                  Frage.lehrheft_id == int(lehrheft_id))).one()

    def arguments(frage):
        return dict(frage_id = frage.id,
                    lehrheft_id = frage.lehrheft_id,
                    fernlehrgang_id = frage.lehrheft.fernlehrgang.id)


class Kursteilnehmer(Base, RDBMixin):
    grok.implements(IKursteilnehmer)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/kursteilnehmer/:kursteilnehmer_id")

    __tablename__ = 'kursteilnehmer'

    id = Column(Integer, Sequence('kursteilnehmer_id'), primary_key=True)
    status = Column(String(50))
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id',))
    #unternehmen_mnr = Column(String(12), ForeignKey('unternehmen.mnr',))

    fernlehrgang = relation(Fernlehrgang, backref = backref('kursteilnehmer', order_by=id))
    teilnehmer = relation(Teilnehmer, backref = backref('kursteilnehmer', order_by=id))
    #unternehmen = relation(Unternehmen, backref = backref('kursteilnehmer', order_by=id))

    def __repr__(self):
        return "<Kursteilnehmer(id='%s', fernlehrgangid='%s')>" %(self.id, self.fernlehrgang_id)

    def factory(fernlehrgang_id, kursteilnehmer_id):
        session = Session()
        return  session.query(Kursteilnehmer).filter(
            and_( Kursteilnehmer.fernlehrgang_id == int(fernlehrgang_id),
                  Kursteilnehmer.id == int(kursteilnehmer_id))).one()

    def arguments(kursteilnehmer):
        return dict(fernlehrgang_id = kursteilnehmer.fernlehrgang_id,
                    kursteilnehmer_id = kursteilnehmer.id)

class Antwort(Base, RDBMixin):
    grok.implements(IAntwort)
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/kursteilnehmer/:kursteilnehmer_id/antwort/:antwort_id")

    __tablename__ = 'antwort'

    id = Column(Integer, Sequence('antwort_seq'), primary_key=True)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id'))
    frage_id = Column(Integer, ForeignKey('frage.id'))
    antwortschema = Column(String(50))
    kursteilnehmer_id = Column(Integer, ForeignKey('kursteilnehmer.id',))

    kursteilnehmer = relation(Kursteilnehmer, 
                              backref = backref('antworten', order_by=frage_id),
                             )

    frage = relation(Frage)
                     

    def __repr__(self):
        return "<Antwort(id='%s', frage='%s', antwort='%s')>" %(self.id, self.frage_id, self.antwortschema)

    def factory(fernlehrgang_id, kursteilnehmer_id, antwort_id):
        session = Session()
        return  session.query(Antwort).filter(
            and_( Antwort.id == int(antwort_id),
                  Antwort.kursteilnehmer_id == int(kursteilnehmer_id))).one()

    def arguments(antwort):
        return dict(antwort_id = antwort.id,
                    kursteilnehmer_id = antwort.kursteilnehmer_id,
                    fernlehrgang_id = antwort.kursteilnehmer.fernlehrgang.id)

