# -*- coding: utf-8 -*-

from zope.schema import *
from cromlech.file import FileField
from zope.interface import Interface, provider
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder


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

    id = Int(
        title=u'Id',
        description=u'Eindeutige Kennzeichnung des ResultatSets',
        required=False,
        readonly=True
        )

    frage = Choice(
        title=u'Frage',
        description=u'Für welche Frage soll das Antwortschema sein.',
        required=True,
        source=reduce_fragen,
        )

    titel = TextLine(
        title=u'Titel',
        description=u'Titel der Frage.',
        required=True,
        )

    beschreibung = Text(
        title=u'Beschreibung',
        required=False,
        )

    bild = FileField(
        title=u"Image",
        description=u"Image to describe the question",
        required=False,
        )
    
    option1 = TextLine(
        title=u'Antwortoption 1',
        description=u'Bitte geben Sie 1. Antwortoption ein.',
        required=True,
        )

    option2 = TextLine(
        title=u'Antwortoption 2',
        description=u'Bitte geben Sie 2. Antwortoption ein.',
        required=True,
        )

    option3 = TextLine(
        title=u'Antwortoption 3',
        description=u'Bitte geben Sie 3. Antwortoption ein.',
        required=True,
        )

    option4 = TextLine(
        title=u'Antwortoption 4',
        description=u'Bitte geben Sie 4. Antwortoption ein.',
        required=True,
        )

    antwortschema = TextLine(
        title=u'Antwortschema',
        description=u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required=True,
        )

    gewichtung = Choice(
        title=u'Gewichtung',
        description=u'Bitte geben Sie die Gewichtung für diese Frage ein.',
        required=True,
        vocabulary=vocabulary((2,2,2),(3,3,3),),
        )
