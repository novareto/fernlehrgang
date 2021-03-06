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
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
import zope.errorview.browser


class IVLWSkinLayer(grok.IDefaultBrowserLayer):
    pass


class IVLWSkin(IVLWSkinLayer, IUVCSkin):
    grok.skin('vlw')


class SystemError(grok.components.ExceptionView):
    """Custom System Error for UVCSITE
    """
    grok.layer(IVLWSkinLayer)

    def render(self):
        return zope.errorview.browser.ExceptionView.render(self)


class APILernwelten(grok.JSON):
    grok.context(IFernlehrgangApp)
    grok.layer(IVLWSkinLayer)

    gbo = GBOAPI()

    @property
    def session(self):
        return Session()

    def hasGBO(self):
        data = simplejson.loads(self.body)
        teilnehmer_id = data.get('teilnehmer_id')
        ret = {}
        ret['teilnehmer_id'] = teilnehmer_id
        ret['gbo'] = False
        if teilnehmer_id:
            teilnehmer = self.session.query(models.Teilnehmer).get(teilnehmer_id)
            mnr = teilnehmer.unternehmen_mnr
            info = self.gbo.get_info(str(mnr))
            if info.status_code == 200:
                ret['gbo'] = True
        return ret

    def checkAuth(self):
        def isVLWTeilnehmer(teilnehmer):
            for ktn in teilnehmer.kursteilnehmer:
                if ktn.fernlehrgang.typ == "4" and ktn.status in ('A1', 'A2'):
                    return True
            return False
        ret = {}
        data = simplejson.loads(self.body)
        teilnehmer_id = data.get('teilnehmer_id')
        ret['teilnehmer_id'] = teilnehmer_id
        ret['gbo'] = False
        if teilnehmer_id:
            teilnehmer = self.session.query(
                models.Teilnehmer).get(teilnehmer_id)
            if not teilnehmer:
                self.response.setStatus(404)
                return 
            vlwtn = isVLWTeilnehmer(teilnehmer)
            if teilnehmer.passwort == data['passwort'] and vlwtn:
                ret['erfolgreich'] = 'true'
            else:
                ret['erfolgreich'] = 'false'
            if not teilnehmer.name or not teilnehmer.email or not teilnehmer.telefon:
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
            if not teilnehmer:
                self.response.setStatus(404)
                return 
            for ktn in teilnehmer.kursteilnehmer:
                if ktn.fernlehrgang.typ == "4":
                    ktns.append(
                        dict(
                            kursteilnehmer_id=ktn.id,
                            fernlehrgang_id=ktn.fernlehrgang_id,
                            titel=ktn.fernlehrgang.titel,
                            jahr=ktn.fernlehrgang.jahr
                            )
                        )
            if teilnehmer:
                oktn = teilnehmer.getVLWKTN()
                ret['teilnehmer_id'] = teilnehmer.id
                ret['name'] = teilnehmer.name
                ret['vorname'] = teilnehmer.vorname
                ret['geburtsdatum'] = str(teilnehmer.geburtsdatum)
                ret['email'] = str(teilnehmer.email)
                ret['telefon'] = str(teilnehmer.telefon)
                ret['unternehmen'] = teilnehmer.unternehmen[0].name
                ret['kurse'] = ktns
                ret['un_klasse'] = oktn.un_klasse
                ret['branche'] = oktn.branche
        return ret

    def setTeilnehmer(self):
        ret = {}
        request = simplejson.loads(self.body)
        #request = self.request
        teilnehmer_id = request.get('teilnehmer_id')
        teilnehmer = self.session.query(models.Teilnehmer).get(teilnehmer_id)
        
        if teilnehmer:
            for field in ITeilnehmer:
                value = request.get(field)
                if value:
                    iField = ITeilnehmer[field]
                    iField.set(teilnehmer, value)
            oktn = teilnehmer.getVLWKTN()
            un_klasse = request.get('un_klasse')
            if un_klasse:
                IKursteilnehmer.get('un_klasse').set(oktn, un_klasse)
            branche = request.get('branche')
            if branche:
                IKursteilnehmer.get('branche').set(oktn, branche)
            if not teilnehmer.name or not teilnehmer.email or not teilnehmer.telefon:
                ret['muss_stammdaten_ergaenzen'] = 'true'
            else:
                ret['muss_stammdaten_ergaenzen'] = 'false'
        else:
            ret = u"Kein Teilnehmer gefunden"
        return ret

    def getCertificate(self):
        teilnehmer_id = self.request.form.get('teilnehmer_id')
        teilnehmer = self.session.query(models.Teilnehmer).get(int(teilnehmer_id))
        ktn = teilnehmer.getVLWKTN()
        je = models.JournalEntry(type="Zertifikat gedrukt", status="1", kursteilnehmer_id=ktn.id)
        teilnehmer.journal_entries.append(je)
        ftf = NamedTemporaryFile()
        from datetime import datetime
        pdate = datetime.now().strftime('%d.%m.%Y')
        try:
            pdate = ktn.antworten[0].datum.strftime('%d.%m.%Y')
        except:
            print "COULD NOT FORMAT DATE"
        fh = createpdf(ftf, {
            'druckdatum': pdate, 
            'flg_titel': ktn.fernlehrgang.titel, 
            'teilnehmer_id': teilnehmer_id,
            'mnr': teilnehmer.stamm_mnr or '',
            'anrede': teilnehmer.anrede,
            'flg_id': str(ktn.fernlehrgang.id),
            'mnr': teilnehmer.unternehmen[0].mnr,
            'vorname': teilnehmer.vorname,
            'name': teilnehmer.name})
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
        kursteilnehmer = self.session.query(models.Kursteilnehmer).get(
            kursteilnehmer_id)
        results = ICalculateResults(kursteilnehmer)
        return results
