# -*- coding: utf-8 -*-
# Copyright (c) 2007-2016 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang import models
from z3c.saconfig import Session
from uvc.layout.layout import IUVCSkin
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer


class IVLWSkinLayer(grok.IDefaultBrowserLayer):
    pass


class IVLWSkin(IVLWSkinLayer, IUVCSkin):
    grok.skin('vlw')


class APILernwelten(grok.JSON):
    grok.context(IFernlehrgangApp)
    grok.layer(IVLWSkinLayer)

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
