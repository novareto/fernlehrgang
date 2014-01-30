# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 


from sqlalchemy import *
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.entity import store_context
from sqlalchemy import TypeDecorator
from sqlalchemy_imageattach.context import get_current_store

from .interfaces.lehrheft import ILehrheft
from .interfaces.flg import IFernlehrgang
from .interfaces.frage import IFrage
from .interfaces.kursteilnehmer import IKursteilnehmer
from .interfaces.unternehmen import IUnternehmen
from .interfaces.teilnehmer import ITeilnehmer
from .interfaces.antwort import IAntwort

from zope.interface import implementer


Base = declarative_base()


class MyStringType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None and dialect.name == "oracle":
            value = value.encode('utf-8')
        return value

    
@implementer(IFernlehrgang)
class Fernlehrgang(Base):

    __tablename__ = 'fernlehrgang'

    id = Column(Integer,
                Sequence('fernlehrgang_seq', start=100, increment=1),
                primary_key=True)
    jahr = Column(String(50))
    titel = Column(String(256))
    typ = Column(String(50))
    beschreibung = Column(String(256))
    punktzahl = Column(Integer(4))
    beginn = Column(Date)
    ende = Column(Date)

    @property
    def title(self):
        return self.jahr 

    def __repr__(self):
        return "<Fernlehrgang(id='%s', jahr='%s', titel='%s')>" % (
            self.id, self.jahr, self.titel)
    

@implementer(IUnternehmen)
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


@implementer(ITeilnehmer)
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

    def __repr__(self):
        return "<Teilnehmer(id='%s', name='%s')>" %(self.id, self.name)


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


@implementer(IFrage)
class Frage(Base):
    __tablename__ = 'frage'

    id = Column(Integer, Sequence('frage_seq', start=10000, increment=1),
                primary_key=True)
    frage = Column(String(5))
    titel = Column(String(256))
    beschreibung = Column(String(500))
    bilder = image_attachment('FrageBild')
    antwortschema = Column(String(50))
    gewichtung = Column(Integer)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id',))
    option1 = Column(String(500))
    option2 = Column(String(500))
    option3 = Column(String(500))
    option4 = Column(String(500))

    lehrheft = relation(
        Lehrheft, 
        backref=backref('fragen', order_by=frage, cascade="all,delete"),
        )

    @property
    def title(self):
        return self.titel
    
    def __repr__(self):
        return "<Frage(id='%s', frage='%s', antwort='%s')>" % (
            self.id, self.frage, self.antwortschema)

    @apply
    def bild():
        """This relies on an implict use of the store.
        read https://sqlalchemy-imageattach.readthedocs.org/en/0.8.1/guide/context.html#implicit-contexts
        """
        def fget(self):
            if self.bilder.count():
                return self.bilder.original
        def fset(self, img):
            if not isinstance(img, Marker):
                if img is None and self.bilder.count():
                    store = get_current_store()
                    for elm in self.bilder:
                        store.delete(elm)
                elif img is not None:
                    self.bilder.from_file(img)
                    self.bilder.generate_thumbnail(height=150)
        return property(fget, fset)

    @property
    def thumbnail(self):
        if self.bilder.count():
            return self.bilder.find_thumbnail(height=150)
        else:
            return None

    

class FrageBild(Base, Image):
    """Question picture model.
    """
    user_id = Column(Integer, ForeignKey(Frage.id), primary_key=True)
    user = relationship('Frage')
    __tablename__ = 'frage_bilder'


@implementer(IKursteilnehmer)
class Kursteilnehmer(Base):
    __tablename__ = 'kursteilnehmer'

    id = Column(Integer,
                Sequence('kursteilnehmer_seq', start=900000, increment=1),
                primary_key=True)
    status = Column(String(50))
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id',))
    unternehmen_mnr = Column(String(12), ForeignKey('adr.MNR',))
    un_klasse = Column(String(3))
    branche = Column(String(5))
    gespraech = Column(String(20))

    fernlehrgang = relation(Fernlehrgang,
                            backref=backref('kursteilnehmer', order_by=id))
    teilnehmer = relation(Teilnehmer,
                          backref=backref('kursteilnehmer', order_by=id))
    unternehmen = relation(Unternehmen,
                           backref=backref('kursteilnehmer', order_by=id))

    @property
    def title(self):
        return "%s %s" % (self.teilnehmer.name, self.teilnehmer.vorname)

    def __repr__(self):
        return "<Kursteilnehmer(id='%s', fernlehrgangid='%s')>" % (
            self.id, self.fernlehrgang_id)


@implementer(IAntwort)
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

    def __repr__(self):
        return "<Antwort(id='%s', frage='%s', antwort='%s')>" % (
            self.id, self.frage_id, self.antwortschema)
