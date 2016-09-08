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
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer


cache = GenericCache()
RESULTS = GenericCache() 


@grok.provider(IContextSourceBinder)
#@cached(cache)
def getTeilnehmerId(context):
    rc = [SimpleTerm(None, None, u'Bitte Auswahl treffen.')]
    session = Session()
    results = session.query(models.Teilnehmer.id, models.Teilnehmer.name, models.Teilnehmer.vorname, models.Teilnehmer.unternehmen_mnr)
    #for tid, name, vname, mnr in results.all():
    for v in RESULTS.values.values():
        tid, name, vname, mnr = v.value
        rc.append(
            SimpleTerm(
                tid,
                tid,
                "%s - %s %s - %s" % (tid, name, vname, mnr)
            )
        )
    return SimpleVocabulary(rc)


@grok.subscribe(ITeilnehmer, IObjectModifiedEvent)
def invalidate_cache(obj, event):
    RESULTS.insert(obj.id, (obj.id, obj.name, obj.vorname, obj.unternehmen_mnr))

@grok.subscribe(IDatabaseOpened)
def fill_cache(*args):
    session = Session()
    results = session.query(models.Teilnehmer.id, models.Teilnehmer.name, models.Teilnehmer.vorname, models.Teilnehmer.unternehmen_mnr)
    for tid, name, vname, mnr in results.all():
        RESULTS.insert(tid, (tid, name, vname, mnr))
    from fernlehrgang.browser.teilnehmer import voc_unternehmen 
    voc_unternehmen(None)
    print "CACHED FILLED"


class ISearch(interface.Interface):

    id = schema.Choice(
        title=u"Teilnehmer ID",
        source=getTeilnehmerId
        )
