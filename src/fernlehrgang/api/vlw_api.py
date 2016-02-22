# -*- coding: utf-8 -*-
# Copyright (c) 2007-2016 NovaReto GmbH
# cklinger@novareto.de

import grok
import simplejson

from .certpdf import createpdf
from base64 import encodestring
from fernlehrgang import models
from z3c.saconfig import Session
from uvc.layout.layout import IUVCSkin
from tempfile import NamedTemporaryFile
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

    def checkAuth(self):
        data = simplejson.loads(self.body)
        teilnehmer_id = data.get('teilnehmer_id')
        if teilnehmer_id:
            teilnehmer = self.session.query(
                models.Teilnehmer).get(teilnehmer_id)
            if teilnehmer.passwort == data['passwort']:
                return teilnehmer.id
        return False

    def getTeilnehmer(self):
        ret = dict()
        ktns = []
        data = simplejson.loads(self.body)
        teilnehmer_id = data.get('teilnehmer_id')
        if teilnehmer_id:
            teilnehmer = self.session.query(
                models.Teilnehmer).get(teilnehmer_id)
            for ktn in teilnehmer.kursteilnehmer:
                ktns.append(
                        dict(
                            kursteilnehmer_id=ktn.id,
                            fernlehrgang_id=ktn.fernlehrgang_id
                            )
                    )
            if teilnehmer:
                ret['teilnehmer_id'] = teilnehmer.id
                ret['name'] = teilnehmer.name
                ret['vorname'] = teilnehmer.vorname
                ret['geburtsdatum'] = str(teilnehmer.geburtsdatum)
                ret['kurse'] = ktns
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

    def getCertificate(self):
        ftf = NamedTemporaryFile()
        fh = createpdf(ftf, {'druckdatum': '01.01.2015'})
        fh.seek(0)
        return encodestring(fh.read())
