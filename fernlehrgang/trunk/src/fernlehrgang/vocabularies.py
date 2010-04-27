# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from fernlehrgang.models import Teilnehmer 
from fernlehrgang.interfaces.frage import IFrage
from fernlehrgang.interfaces.antwort import IAntwort 
from zope.schema.interfaces import IVocabularyFactory
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.lehrheft import ILehrheft
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


def vocabulary(*terms):
    """ """
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


class UnternehmenSources(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'unternehmen')
    
    def __call__(self, context):
        rc = []
        session = Session()
        for id, name, vorname in session.query(Teilnehmer.id, Teilnehmer.name, Teilnehmer.vorname).all():
            value = "%s - %s %s" % (id, name, vorname)
            rc.append(SimpleTerm(id, value, value))
        return SimpleVocabulary(rc)    


class LehrheftSources(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'LehrheftVocab')
    
    def __call__(self, context):
        rc = []
        if IAntwort.providedBy(context):
            fernlehrgang = context.kursteilnehmer.fernlehrgang
        if IKursteilnehmer.providedBy(context):
            fernlehrgang = context.fernlehrgang
        for lehrheft in fernlehrgang.lehrhefte:
            value = "%s - %s" % (lehrheft.nummer, lehrheft.titel)
            rc.append(SimpleTerm(lehrheft.id, lehrheft.id, value))
        return SimpleVocabulary(rc)    


class FragenSources(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'FragenVocab')
    
    def __call__(self, context):
        session = Session()
        rc = [SimpleTerm(0, 'Bitte eine Auswahl treffen', 'Bitte eine Auswahl treffen')]
        if IAntwort.providedBy(context):
            fernlehrgang = context.kursteilnehmer.fernlehrgang
        if IKursteilnehmer.providedBy(context):
            fernlehrgang = context.fernlehrgang
        for lehrheft in fernlehrgang.lehrhefte:
            for frage in lehrheft.fragen: 
                term = "%s - %s" %(frage.frage, frage.titel)
                rc.append(SimpleTerm(frage.id, term, term))           
        return SimpleVocabulary(rc)    


class ReduceFrageSource(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'ReduceFrageVocab')
    
    def __call__(self, context):
        rc = []
        alle = range(1, 11)
        if ILehrheft.providedBy(context):
            fragen = context.fragen
        if IFrage.providedBy(context):
            fragen = context.lehrheft.fragen
        reduce = [int(x.frage) for x in fragen]
        for x in alle:
            if x not in reduce:
                rc.append(SimpleTerm(str(x), str(x), str(x)))
        return SimpleVocabulary(rc)   


class ReduceLehrheftSource(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'ReduceLehrheftVocab')
    
    def __call__(self, context):
        rc = []
        alle = range(1, 11)
        if ILehrheft.providedBy(context):
            lehrhefte = context.fernlehrgang.lehrhefte
        if IFernlehrgang.providedBy(context):
            lehrhefte = context.lehrhefte
        reduce = [x.nummer for x in lehrhefte]
        for x in alle:
            if x not in reduce:
                rc.append(SimpleTerm(str(x), str(x), str(x)))
        return SimpleVocabulary(rc)   
