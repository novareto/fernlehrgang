# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import grokcore.component as grok

from z3c.saconfig import Session
from fernlehrgang import models
from zope import interface, schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from GenericCache import GenericCache
from GenericCache.decorators import cached
from zope.processlifetime import IDatabaseOpened

cache = GenericCache()
RESULTS = {}


@grok.provider(IContextSourceBinder)
#@cached(cache)
def getTeilnehmerId(context):
    rc = [SimpleTerm(None, None, u'Bitte Auswahl treffen.')]
    session = Session()
    results = session.query(models.Teilnehmer.id, models.Teilnehmer.name, models.Teilnehmer.vorname, models.Teilnehmer.unternehmen_mnr)
    #for tid, name, vname, mnr in results.all():
    for tid, name, vname, mnr in RESULTS.values():
        rc.append(
            SimpleTerm(
                tid,
                tid,
                "%s - %s %s - %s" % (tid, name, vname, mnr)
            )
        )
    return SimpleVocabulary(rc)


from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer

@grok.subscribe(ITeilnehmer, IObjectModifiedEvent)
def invalidate_cache(obj, event):
    RESULTS[obj.id] = (obj.id, obj.name, obj.vorname, obj.unternehmen_mnr)

@grok.subscribe(IDatabaseOpened)
def fill_cache(*args):
    session = Session()
    results = session.query(models.Teilnehmer.id, models.Teilnehmer.name, models.Teilnehmer.vorname, models.Teilnehmer.unternehmen_mnr)
    for tid, name, vname, mnr in results.all():
        RESULTS[tid] = (tid, name, vname, mnr)
    #getTeilnehmerId(None)
    from fernlehrgang.browser.teilnehmer import voc_unternehmen 
    voc_unternehmen(None)
    print "CACHED FILLED"


class ISearch(interface.Interface):

    id = schema.Choice(
        title=u"Teilnehmer ID",
        source=getTeilnehmerId
        )
