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


@grok.provider(IContextSourceBinder)
@cached(cache)
def getTeilnehmerId(context):
    rc = [SimpleTerm(None, None, u'Bitte Auswahl treffen.')]
    session = Session()
    results = session.query(models.Teilnehmer.id, models.Teilnehmer.name, models.Teilnehmer.vorname)
    for tid, name, vname in results.all():
        rc.append(
            SimpleTerm(
                tid,
                tid,
                "%s - %s %s" % (tid, name, vname)
            )
        )
    return SimpleVocabulary(rc)


@grok.subscribe(IDatabaseOpened)
def fill_cache(*args):
    getTeilnehmerId(None)
    print "CACHED FILLED"


class ISearch(interface.Interface):

    id = schema.Choice(
        title=u"Teilnehmer ID",
        source=getTeilnehmerId
        )
