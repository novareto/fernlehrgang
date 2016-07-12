# -*- coding: utf-8 -*-
# Copyright (c) 2007-2016 NovaReto GmbH
# cklinger@novareto.de

import grok
import simplejson

from .gbo import GBOAPI
from .certpdf import createpdf
from base64 import encodestring
from fernlehrgang import models
from z3c.saconfig import Session
from uvc.layout.layout import IUVCSkin
from tempfile import NamedTemporaryFile
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults


class IVLWSkinLayer(grok.IDefaultBrowserLayer):
    pass


class IVLWSkin(IVLWSkinLayer, IUVCSkin):
    grok.skin('vlw')


class APILernwelten(grok.JSON):
    grok.context(IFernlehrgangApp)
    grok.layer(IVLWSkinLayer)

    gbo = GBOAPI()

    @property
    def session(self):
        return Session()

    def checkAuth(self):
        ret = {}
        data = simplejson.loads(self.body)
        teilnehmer_id = data.get('teilnehmer_id')
        ret['teilnehmer_id'] = teilnehmer_id
        ret['gbo'] = False
        if teilnehmer_id:
            teilnehmer = self.session.query(
                models.Teilnehmer).get(teilnehmer_id)
            if teilnehmer.passwort == data['passwort']:
                ret['erfolgreich'] = 'true'
            else:
                ret['erfolgreich'] = 'false'
            if not teilnehmer.name:
                ret['muss_stammdaten_ergaenzen'] = 'true'
            else:
                ret['muss_stammdaten_ergaenzen'] = 'false'
            mnr = teilnehmer.unternehmen_mnr
            info = self.gbo.get_info(str(mnr))
            if info.status_code == 200:
                ret['gbo'] = True
        return ret 

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

    def getResults(self):
        data = simplejson.loads(self.body)
        kursteilnehmer_id = data.get('kursteilnehmer_id')
        results = self._getResults(kursteilnehmer_id)
        return results.summary()

    def getLehrhefte(self):
        data = simplejson.loads(self.body)
        kursteilnehmer_id = data.get('kursteilnehmer_id')
        results = self._getResults(kursteilnehmer_id)
        return results.lehrhefte()

    def _getResults(self, kursteilnehmer_id=900000):
        kursteilnehmer = self.session.query(models.Kursteilnehmer).get(kursteilnehmer_id)
        results = ICalculateResults(kursteilnehmer)
        return results
