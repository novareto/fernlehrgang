# -*- coding: utf-8 -*-
# Copyright (c) 2007-2016 NovaReto GmbH
# cklinger@novareto.de

import grok

from zope import interface
from fernlehrgang import models
from z3c.saconfig import Session
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer

from zope.publisher.interfaces.browser import IHTTPRequest
from zope.traversing.interfaces import ITraversable


from nva.mq import reader
from nva.mq.interfaces import IListener


grok.global_utility(reader.BaseReader, IListener, direct=True)


def test_processor(queue, name):
    def info_processor(body, message, **data):
        print body, message, data
    return info_processor


class Traverser(grok.MultiAdapter):
    grok.provides(ITraversable)
    grok.name('++create++')
    grok.adapts(interface.Interface, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        import pdb; pdb.set_trace()


class APILernwelten(grok.JSON):
    grok.context(IFernlehrgangApp)

    @property
    def session(self):
        return Session()

    def getTeilnehmer(self):
        ret = dict()
        teilnehmer_id = self.request.get('teilnehmer_id')
        teilnehmer = self.session.query(models.Teilnehmer).get(teilnehmer_id)
        if teilnehmer:
            ret['teilnehmer_id'] = teilnehmer.id
            ret['name'] = teilnehmer.name
            ret['vorname'] = teilnehmer.vorname
            ret['geburtsdatum'] = str(teilnehmer.geburtsdatum)
            ret['passwort'] = teilnehmer.passwort
        return ret

    def setTeilnehmer(self):
        request = self.request
        teilnehmer_id = request.get('teilnehmer_id')
        teilnehmer = self.session.query(models.Teilnehmer).get(teilnehmer_id)
        if teilnehmer:
            for field in ITeilnehmer:
                value = request.get(field)
                if value:
                    iField = ITeilnehmer[field]
                    iField.set(teilnehmer, value)
