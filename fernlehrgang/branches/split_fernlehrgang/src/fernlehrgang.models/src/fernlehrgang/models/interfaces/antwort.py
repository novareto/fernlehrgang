# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de

from datetime import datetime
from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder

from . import named_vocabulary
from .kursteilnehmer import IKursteilnehmer
from .frage import IFrage


def vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


class IAntwort(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung der Antwort',
        required = False,
        readonly = True
        )

    lehrheft_id = Choice(
        title = u'Lehrheft',
        description = u'Für welches Lehrheft liegt eine Antwort vor.',
        required = True,
        source = named_vocabulary('lehrheft'),
        )

    frage_id = Choice(
        title = u'Frage',
        description = u'Für welche Frage soll das Antwortschema sein.',
        required = True,
        source = named_vocabulary('fragen'),
        )

    antwortschema = TextLine(
        title = u'Antwortschema',
        description = u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required = True,
        default = u'',
        )

    datum = Datetime(
        title = u'Datum',
        description = u'Modifikationsdatum',
        required = False,
        readonly = False,
        defaultFactory = datetime.now,
        default = datetime.now(),
        )

    system = Choice(
        title = u'Eingabesystem',
        description = (u'Bitte geben Sie an wie diese Antwort ins ' +
                       u'System gekommen ist.'),
        required = True,
        vocabulary=vocabulary(
            ('FernlehrgangApp', 'FernlehrgangApp', 'FernlehrgangApp'),
            ('Extranet', 'Extranet', 'Extranet'),
            ),
        )
