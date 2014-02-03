# -*- coding: utf-8 -*-

from cromlech.file import FileField
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


def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title)
                             for value, token, title in terms])


@provider(IContextSourceBinder)
def reduce_fragen(context):
    from .lehrheft import ILehrheft
    rc = []
    reduce = []
    alle = range(1, 11)
    if ILehrheft.providedBy(context):
        fragen = context.fragen
        reduce = [int(x.frage) for x in fragen]
    if IFrage.providedBy(context):
        fragen = context.lehrheft.fragen
    for x in alle:
        if x not in reduce:
            rc.append(SimpleTerm(str(x), str(x), str(x)))
    return SimpleVocabulary(rc)   


class IFrage(Interface):

    id = zope.schema.Int(
        title=u'Id',
        description=u'Eindeutige Kennzeichnung des ResultatSets',
        required=False,
        readonly=True
        )

    frage = zope.schema.Choice(
        title=u'Frage',
        description=u'Für welche Frage soll das Antwortschema sein.',
        required=True,
        source=reduce_fragen,
        )

    titel = zope.schema.TextLine(
        title=u'Titel',
        description=u'Titel der Frage.',
        required=True,
        )

    beschreibung = zope.schema.Text(
        title=u'Beschreibung',
        required=False,
        )

    bild = FileField(
        title=u"Image",
        description=u"Image to describe the question",
        required=False,
        )
    
    option1 = zope.schema.TextLine(
        title=u'Antwortoption 1',
        description=u'Bitte geben Sie 1. Antwortoption ein.',
        required=True,
        )

    option2 = zope.schema.TextLine(
        title=u'Antwortoption 2',
        description=u'Bitte geben Sie 2. Antwortoption ein.',
        required=True,
        )

    option3 = zope.schema.TextLine(
        title=u'Antwortoption 3',
        description=u'Bitte geben Sie 3. Antwortoption ein.',
        required=True,
        )

    option4 = zope.schema.TextLine(
        title=u'Antwortoption 4',
        description=u'Bitte geben Sie 4. Antwortoption ein.',
        required=True,
        )

    antwortschema = zope.schema.TextLine(
        title=u'Antwortschema',
        description=u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required=True,
        )

    gewichtung = zope.schema.Choice(
        title=u'Gewichtung',
        description=u'Bitte geben Sie die Gewichtung für diese Frage ein.',
        required=True,
        vocabulary=vocabulary((2,2,2),(3,3,3),),
        )


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
