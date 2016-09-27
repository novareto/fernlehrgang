# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import os
import grokcore.component as grok

from z3c.saconfig import Session
from fernlehrgang import models
from zope import interface, schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from GenericCache import GenericCache
from GenericCache.decorators import cached
from zope.processlifetime import IDatabaseOpened
from zope.lifecycleevent.interfaces import IObjectModifiedEvent, IObjectAddedEvent
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from profilehooks import profile
from fernlehrgang import log


cache = GenericCache()


class Vocabulary(SimpleVocabulary):

    def add(self, term):
        if term.value in self.by_value:
            raise ValueError(
                'term values must be unique: %s' % repr(term.value))
        if term.token in self.by_token:
            raise ValueError(
                'term tokens must be unique: %s' % repr(term.token))
        self._terms.append(term)
        self.by_value[term.value] = term
        self.by_token[term.token] = term

    def delete(self, term):
        del self.by_value[term.value]
        del self.by_token[term.token]
        self._terms.remove(term)


VOCABULARY = None
        

@grok.provider(IContextSourceBinder)
def getTeilnehmerId(context):
    return VOCABULARY


@grok.subscribe(ITeilnehmer, IObjectModifiedEvent)
def update_cache(obj, event):
    term = VOCABULARY.getTermByToken(str(obj.id))
    term.title = u'%s - %s %s - %s' % (
        obj.id, obj.name, obj.vorname, obj.unternehmen_mnr)
    

@grok.subscribe(ITeilnehmer, IObjectAddedEvent)
def add_in_cache(obj, event):
    title = u'%s - %s %s - %s' % (
        obj.id, obj.name, obj.vorname, obj.unternehmen_mnr)
    term = SimpleTerm(title=title, token=obj.id, value=obj.id)
    global VOCABULARY
    VOCABULARY.add(term)
    

@grok.subscribe(IDatabaseOpened)
def fill_cache_teilnehmer(*args):
    session = Session()
    results = session.query(
        models.Teilnehmer.id, 
        models.Teilnehmer.name, 
        models.Teilnehmer.vorname, 
        models.Teilnehmer.unternehmen_mnr).order_by(models.Teilnehmer.name, models.Teilnehmer.vorname)
    print os.environ.get('DEBUG')
    if os.environ.get('DEBUG'):
        print "I FILTER IT NOW"
        results = results.filter(models.Teilnehmer.unternehmen_mnr == 995000221)
    terms = [SimpleTerm(
        title=u'%s - %s %s - %s' % (tid, name, vname, mnr),
        token=tid,
        value=tid) for tid, name, vname, mnr in results.all()]
    terms = [SimpleTerm(None, None, u'Bitte Auswahl treffen.')] + terms
    global VOCABULARY
    VOCABULARY = Vocabulary(terms)
    log(u'Der Cache für die Teilnehmer ist gefüllt')
 

@grok.subscribe(IDatabaseOpened)
def fill_cache_unternehmen(*args):
    from fernlehrgang.browser.teilnehmer import voc_unternehmen 
    voc_unternehmen(None)
    log(u'Der Cache für Unternehmen ist gefüllt')

    
class ISearch(interface.Interface):

    id = schema.Choice(
        title=u"Teilnehmer ID",
        source=getTeilnehmerId
        )
