# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grokcore.component as grok

from z3c.saconfig import Session
from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.frage import IFrage

import datetime

def today():
    return datetime.date.today()


@grok.provider(IContextSourceBinder)
def lehrheft_vocab(context):    
    rc = [SimpleTerm(0, 'Bitte eine Auswahl treffen', 'Bitte eine Auswahl treffen')]
    if IAntwort.providedBy(context):
        fernlehrgang = context.kursteilnehmer.fernlehrgang
    if IKursteilnehmer.providedBy(context):
        fernlehrgang = context.fernlehrgang
    for lehrheft in fernlehrgang.lehrhefte:
        value = "%s - %s" % (lehrheft.nummer, lehrheft.titel)
        rc.append(SimpleTerm(lehrheft.id, lehrheft.id, value))
    return SimpleVocabulary(rc)    


@grok.provider(IContextSourceBinder)
def fragen_vocab(context):
    session = Session()
    rc = [SimpleTerm(0, 'Bitte eine Auswahl treffen', 'Bitte eine Auswahl treffen')]
    if IAntwort.providedBy(context):
        fernlehrgang = context.kursteilnehmer.fernlehrgang
    if IKursteilnehmer.providedBy(context):
        fernlehrgang = context.fernlehrgang
    for lehrheft in fernlehrgang.lehrhefte:
        for frage in lehrheft.fragen: 
            term = "%s - %s" %(frage.frage, frage.titel)
            rc.append(SimpleTerm(frage.id, frage.id, term))           
    return SimpleVocabulary(sorted(rc, key=lambda term: term.value))    


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
        source = lehrheft_vocab,
        )

    frage_id = Choice(
        title = u'Frage',
        description = u'Für welche Frage soll das Antwortschema sein.',
        required = True,
        source = fragen_vocab,
        )

    antwortschema = TextLine(
        title = u'Antwortschema',
        description = u'Bitte geben Sie Antwortmöglichkeiten ein.',
        required = True,
        default = u'',
        )

    gbo = TextLine(
        title = u'GBO',
        description = u'TO BE DONE',
        required = False,
        )

    gbo_daten = Bytes(
        title = u"GBO-Daten",
        description = u"JSON-GBO Datenstreamm der vlw",
        required = False,
        )

    datum = Date(
        title = u'Datum',
        description = u'Modifikationsdatum',
        required = False,
        readonly = False,
        defaultFactory = today,
        )

    system = Choice(
        title = u'Eingabesystem',
        description = u'Bitte geben Sie an wie diese Antwort ins System gekommen ist.',
        required = True,
        vocabulary=vocabulary(
            ('FernlehrgangApp', 'FernlehrgangApp', 'FernlehrgangApp'),
            ('Extranet', 'Extranet', 'Extranet'),
            ('Virtuelle Lernwelt', 'Virtuelle Lernwelt', 'Virtuelle Lernwelt')
        )
        )
