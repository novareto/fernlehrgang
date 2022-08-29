# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de


import grok
import datetime

from megrok import traject
from fernlehrgang import log

from sqlalchemy import *
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

from fernlehrgang.interfaces.antwort import IAntwort
from fernlehrgang.interfaces.journal import IJournalEntry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.frage import IFrage
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.kursteilnehmer import IVLWKursteilnehmer
from fernlehrgang.interfaces.kursteilnehmer import IFortbildungKursteilnehmer
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from megrok import traject
from plone.memoize import ram, instance
from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, relation, backref
from z3c.saconfig import Session
from z3c.saconfig.interfaces import IEngineCreatedEvent
from zope.container.contained import Contained
from zope.dublincore.interfaces import IDCDescriptiveProperties
from sqlalchemy import event
from zope.interface import alsoProvides, Interface, implementer
from z3c.saconfig import EngineFactory, GloballyScopedSession
from zope.app.appsetup.product import getProductConfiguration


class IContent(Interface):
    pass


config = getProductConfiguration('database')
SCHEMA = config['schema'] or None 
#SCHEMA = "FLGUTF8"
log('Database SCHEMA --> %s' % SCHEMA)
Base = declarative_base()
Base.metadata.schema = SCHEMA 


class MyStringType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None and dialect.name == "oracle":
            value = value.encode('utf-8')
        return value


@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    metadata = Base.metadata
    metadata.create_all(event.engine, checkfirst=True)


@implementer(IContent)
class RDBMixin(traject.Model, Contained):
    """ Base Mixin for RDB-Base Classes """
    grok.baseclass()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Account(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("account/:user_id")
    __tablename__ = 'accounts'

    login = Column(String(50), primary_key=True)
    email = Column(String(50))
    real_name = Column(String(100))
    role = Column(String(100))
    password = Column('kennwort', String(100))

    def checkPassword(self, password):
        if password == self.password:
            return True
        return False

    def getEmail(self):
        if hasattr(self, 'email'):
            return self.email
        return ''

    def factory(user_id):
        session = Session()
        return session.query(Account).filter(
            Account.login == user_id).one()

    def arguments(account):
        return dict(login = account.login)


@implementer(IFernlehrgang, IDCDescriptiveProperties)
class Fernlehrgang(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id")

    __tablename__ = 'fernlehrgang'

    id = Column(Integer, Sequence('fernlehrgang_seq', start=100, increment=1, schema=SCHEMA), primary_key=True)
    jahr = Column(String(50))
    titel = Column(String(256))
    typ = Column(String(50))
    beschreibung = Column(String(256))
    punktzahl = Column(Integer())
    beginn = Column(Date)
    ende = Column(Date)

    @property
    def title(self):
        return self.jahr

    def __repr__(self):
        return "<Fernlehrgang(id='%s', jahr='%s', titel='%s')>" %(self.id, self.jahr, self.titel)

    def factory(fernlehrgang_id):
        session = Session()
        return session.query(Fernlehrgang).filter(
            Fernlehrgang.id == int(fernlehrgang_id)).one()

    def arguments(fernlehrgang):
        return dict(fernlehrgang_id = fernlehrgang.id)


@implementer(IUnternehmen, IDCDescriptiveProperties)
class Unternehmen(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("unternehmen/:unternehmen_mnr")
    #grok.traversable(attr='god_data')

    __tablename__ = 'adr'
    #__tablename__ = 'adr_transfer'

    #id = Column("ID", Numeric, primary_key=True)
    mnr = Column("MNR", String(11), primary_key=True, index=True)
    name = Column("NAME1", String(33))
    name2 = Column("NAME2", String(33))
    name3 = Column("NAME3", String(33))
    str = Column("STR", String(70))
    plz = Column("PLZ", String(10))
    ort = Column("ORT", String(30))
    betriebsart = Column("BETRIEBSART", String(1))
    mnr_e = Column("MNR_E", MyStringType(12))
    mnr_g_alt = Column("MNR_G_ALT", MyStringType(12))
    aktiv = Column("aktiv", Boolean())
    b_groesse = Column('BETRIEBSGROESSE', String(240))
    hbst = Column('HBST', String(9))

    @property
    def title(self):
        return self.mnr

    def __repr__(self):
        return "<Unternehmen(mnr='%s')>" %(self.mnr)

    def factory(unternehmen_mnr):
        session = Session()
        return session.query(Unternehmen).filter(
            Unternehmen.mnr == unternehmen_mnr).one()

    def arguments(unternehmen):
        return dict(unternehmen_mnr = unternehmen.mnr)



unternehmen_teilnehmer = Table(
    'unternehmen_teilnehmer', Base.metadata,
    Column('unternehmen_id', String(11), ForeignKey('adr.MNR')),
    #Column('unternehmen_id', String(11), ForeignKey('adr_transfer.MNR')),
    Column('teilnehmer_id', Integer, ForeignKey('teilnehmer.id'))
)


@implementer(ITeilnehmer, IDCDescriptiveProperties)
class Teilnehmer(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("unternehmen/:unternehmen_mnr/teilnehmer/:id")

    __tablename__ = 'teilnehmer'

    id = Column(Integer, Sequence('teilnehmer_seq', start=100000, increment=1, schema=SCHEMA), primary_key=True)

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
    stamm_mnr = Column(String(20))
    
    unternehmen_mnr = Column(String(11), ForeignKey(Unternehmen.mnr))

    #unternehmen = relation(Unternehmen,
    #                       backref = backref('teilnehmer', order_by=id))

    unternehmen = relationship(
        "Unternehmen",
        secondary=unternehmen_teilnehmer, backref="teilnehmer"
        )

    @property
    def title(self):
        return "%s %s" % (self.name, self.vorname)

    def __repr__(self):
        return "<Teilnehmer(id='%s', name='%s')>" %(self.id, self.id)

    def getVLWKTN(self):
        for ktn in self.kursteilnehmer:
            if ktn.fernlehrgang.typ == '4':
                return ktn

    def factory(id, unternehmen_mnr):
        session = Session()
        return session.query(Teilnehmer).filter(
            and_(Teilnehmer.id == int(id), Teilnehmer.unternehmen_mnr == unternehmen_mnr)).one()

    def arguments(teilnehmer):
        return dict(id = teilnehmer.id, unternehmen_mnr = teilnehmer.unternehmen_mnr)


@implementer(ILehrheft, IDCDescriptiveProperties)
class Lehrheft(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id")

    __tablename__ = 'lehrheft'

    id = Column(Integer, Sequence('lehrheft_seq', start=1000, increment=1, schema=SCHEMA), primary_key=True)
    nummer = Column(String(5))
    titel = Column(String(256))
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))

    fernlehrgang = relation(Fernlehrgang,
                            backref = backref('lehrhefte', order_by=nummer.asc(), cascade="all,delete"),
                           )

    @property
    def title(self):
        return self.titel

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


@implementer(IFrage, IDCDescriptiveProperties)
class Frage(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id/frage/:frage_id")

    __tablename__ = 'frage'

    id = Column(Integer, Sequence('frage_seq', start=10000, increment=1, schema=SCHEMA), primary_key=True)
    frage = Column(String(5))
    titel = Column(String(256))
    antwortschema = Column(String(50))
    gewichtung = Column(Integer)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id',))

    lehrheft = relation(Lehrheft,
                        backref = backref('fragen', order_by=frage, cascade="all,delete"),
                        )

    @property
    def title(self):
        return self.titel

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


@implementer(IKursteilnehmer, IDCDescriptiveProperties)
class Kursteilnehmer(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/kursteilnehmer/:kursteilnehmer_id")

    __tablename__ = 'kursteilnehmer'

    id = Column(Integer, Sequence('kursteilnehmer_seq', start=900000, increment=1, schema=SCHEMA), primary_key=True)
    status = Column(String(50))
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id',))
    #unternehmen_mnr = Column(String(11), ForeignKey('adr_transfer.MNR',))
    unternehmen_mnr = Column(String(11), ForeignKey('adr.MNR',))
    erstell_datum = Column(DateTime, default=datetime.datetime.now)
    gespraech = Column(String(20))
    un_klasse = Column(String(20))
    branche = Column(String(20))
    fixed_results = Column(String(100))
    #fixed_results = None

    fernlehrgang = relation(Fernlehrgang, backref = backref('kursteilnehmer', order_by=id), lazy="joined")
    teilnehmer = relation(Teilnehmer, backref = backref('kursteilnehmer', order_by=id), lazy="joined")
    unternehmen = relation(Unternehmen, backref = backref('kursteilnehmer', order_by=id))

    @property
    def title(self):
        return "%s %s" % (self.teilnehmer.name, self.teilnehmer.vorname)

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

    @property
    def result(self):
        from fernlehrgang.interfaces.resultate import ICalculateResults
        return ICalculateResults(self).summary()


# standard decorator style
@event.listens_for(Kursteilnehmer, 'load')
def receive_load(target, context):
    if target.fernlehrgang.typ == "4":
        alsoProvides(target, IVLWKursteilnehmer)
    elif target.fernlehrgang.typ in ("3", "5"):
        alsoProvides(target, IFortbildungKursteilnehmer)


@implementer(IAntwort, IDCDescriptiveProperties)
class Antwort(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("fernlehrgang/:fernlehrgang_id/kursteilnehmer/:kursteilnehmer_id/antwort/:antwort_id")

    __tablename__ = 'antwort'
    #__table_args__ = (UniqueConstraint('frage_id', 'kursteilnehmer_id', name="unique_frage"), {})

    id = Column(Integer, Sequence('antwort_seq', start=100000, increment=1, schema=SCHEMA), primary_key=True)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id'))
    frage_id = Column(Integer, ForeignKey('frage.id'))
    antwortschema = Column(String(50))
    datum = Column(DateTime)
    system = Column("SYSTEMWERT", String(50))
    gbo = Column(String(50))
    gbo_daten = Column(LargeBinary)
    kursteilnehmer_id = Column(Integer, ForeignKey('kursteilnehmer.id',))

    kursteilnehmer = relation(Kursteilnehmer,
                              backref = backref('antworten', lazy='joined', order_by=frage_id, cascade="all,delete"),
                             )

    frage = relation(Frage, lazy="joined")

    @property
    def title(self):
        return self.frage.titel

    @property
    def rlhid(self):
        return self.frage.lehrheft_id

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


@implementer(IJournalEntry)
class JournalEntry(Base, RDBMixin):
    grok.context(IFernlehrgangApp)
    traject.pattern("unternehmen/:unternehmen_mnr/teilnehmer/:id/journal/:jid")

    __tablename__ = 'journal'

    id = Column(Integer, primary_key=True)
    teilnehmer_id = Column(Integer, ForeignKey(Teilnehmer.id))
    creation_date = Column(DateTime, default=datetime.datetime.now)
    status = Column(String(50))
    type = Column(String(500))
    kursteilnehmer_id = Column(Integer, ForeignKey(Kursteilnehmer.id))
    teilnehmer = relationship(Teilnehmer, backref=backref("journal_entries", order_by='JournalEntry.id.desc()'))
    kursteilnehmer = relationship(Kursteilnehmer)

    @property
    def date(self):
        return self.creation_date

    def __repr__(self):
        return "<JournalEntry(id='%i', teilnehmer='%i')>" % (
            self.id, self.teilnehmer_id)

    def factory(unternehmen_mnr, id, jid):
        session = Session()
        return session.query(JournalEntry).filter(
            and_(JournalEntry.id == jid,
                 JournalEntry.teilnehmer_id == id)).one()

            #     JournalEntry.teilnehmer.unternehmen_mnr==unternehmen_mnr)).one()

    def arguments(entry):
        return dict(
            jid=entry.id,
            id=entry.teilnehmer.id,
            unternehmen_mnr=entry.teilnehmer.unternehmen_mnr)
