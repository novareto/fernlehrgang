
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

class Fernlehrgaenge(Base, grok.Context):
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


class Lehrhefte(Base, grok.Context):
    __table_name__ = 'lehrheft'

    id = Column(Integer, primary_key=True)
    nummer = Colum(Integer)
    fernlehrgang_id = Column(Integer, ForeignKey('Fernlehrgaenge.id'))

    lehrheft = relation(Fernlehrgaenge, backref = backref('lehrhefte', order_by=nummer))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Lehrgang(id='%s', nummer='%s', fernlehrgangid='%s')>" %(self.id, self.nummer, self.fernlehrgang_id)
