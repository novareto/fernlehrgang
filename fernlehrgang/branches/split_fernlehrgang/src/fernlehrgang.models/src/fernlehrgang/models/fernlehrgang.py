# -*- coding: utf-8 -*-

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


@provider(IContextSourceBinder)
def jahre(context):
    items = []
    for jahr in range(2011, 2020, 1):
        jahr = str(jahr)
        items.append(SimpleTerm(jahr, jahr, jahr))
    return SimpleVocabulary(items)


@provider(IContextSourceBinder)
def typ(context):
    return SimpleVocabulary((
        SimpleTerm('1', '1', 'Fernlehrgang'),
        SimpleTerm('2', '2', 'Online Fernlehrgang'),
        SimpleTerm('3', '3', 'Fortbildung'),
        ))


class IFernlehrgang(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des Fernlehrgangs',
        required = False,
        readonly = True
        )

    jahr = Choice(
        title = u'Jahr',
        description = u'Das Jahr in dem der Fernlehrgang stattfindent',
        required = True,
        source = jahre,
        )

    titel = TextLine(
        title = u'Titel',
        description = u'Titel des Fernlehrgangs',
        required = True
        )

    beschreibung = Text(
        title = u'Beschreibung',
        description = u'Beschreibung des Fernlehrgangs',
        required = True
        )

    typ = Choice(
        title = u'Typ des Fernlehrgang',
        description = u'Bitte wählen Sie den Typ des Fernlehrgangs aus',
        source = typ,
        required = True
        )

    punktzahl = Int(
        title = u'Punkteanzahl',
        description = u'Bitte geben Sie hier die Punkteanzahl an, die '
                       'erreicht werden muss, um den Fernlehrgang zu bestehen',
        required = True
        )

    beginn = Date(title = u'Start',
        description = u'Zu welchem Datum soll der Fernlehrgang beginnen?',
        required = True
        )

    ende = Date(title = u'Ende',
        description = u'Zu welchem Datum soll der Fernlehrgang enden?',
        required = True
        )


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
