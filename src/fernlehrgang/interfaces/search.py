# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import grokcore.component as grok

from z3c.saconfig import Session
from fernlehrgang import models
from zope import interface, schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@grok.provider(IContextSourceBinder)
def getTeilnehmerId(context):
    rc = [SimpleTerm(None, None, u'Bitte Auswahl treffen.')]
    session = Session()
    teilnehmer = session.query(models.Teilnehmer)
    for tn in teilnehmer.all():
        rc.append(
            SimpleTerm(
                tn.id,
                tn.id,
                "%s %s" % (tn.id, tn.name)
            )
        )
    return SimpleVocabulary(rc)


class ISearch(interface.Interface):

    id = schema.Choice(
        title=u"Teilnehmer ID",
        source=getTeilnehmerId
        )
