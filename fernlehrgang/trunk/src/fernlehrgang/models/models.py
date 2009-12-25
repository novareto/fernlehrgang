
import grok

from sqlalchemy import *
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

from z3c.saconfig.interfaces import IEngineCreatedEvent


@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    metadata = Base.metadata
    metadata.create_all(event.engine)


Base = declarative_base()

class Fernlehrgang(Base, grok.Context):
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


class Lehrheft(Base, grok.Context):
    __tablename__ = 'lehrheft'

    id = Column(Integer, primary_key=True)
    nummer = Column(Integer)
    fernlehrgang_id = Column(Integer, ForeignKey('fernlehrgang.id',))

    lehrheft = relation(Fernlehrgang, backref = backref('lehrhefte', order_by=nummer))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Lehrgang(id='%s', nummer='%s', fernlehrgangid='%s')>" %(self.id, self.nummer, self.fernlehrgang_id)


class Resultat(Base, grok.Context):
    __tablename__ = 'resultat'

    id = Column(Integer, primary_key=True)
    frage = Column(Integer)
    antwortschema = Column(String)
    lehrheft_id = Column(Integer, ForeignKey('lehrheft.id',))

    resultat = relation(Lehrheft, backref = backref('resultate', order_by=frage))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Resultat(id='%s', frage='%s', antwort='%s')>" %(self.id, self.frage, self.antwortschema)
