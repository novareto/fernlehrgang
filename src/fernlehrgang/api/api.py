# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import json
import datetime

from sqlalchemy import *
from z3c.saconfig import Session
from fernlehrgang.models import Frage, Teilnehmer, Antwort, Kursteilnehmer
from fernlehrgang.app import RestLayer, KPTZLayer
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults


#
### XMLRPC
#

class HelperAPI(grok.XMLRPC):
    grok.context(IFernlehrgangApp)

    def getFlgIds(self, teilnehmer_id):
        session = Session()
        ret = session.query(Kursteilnehmer.fernlehrgang_id).filter(
                Kursteilnehmer.teilnehmer_id == teilnehmer_id)
        return ret.all()

    def getFrageIds(self, lehrheft_id):
        session = Session()
        d = dict()
        ret = session.query(Frage).filter(Frage.lehrheft_id==lehrheft_id)
        for frage in ret.all():
            d[frage.frage] = frage.id
        return d

    def getMNRFromTeilnehmerID(self, teilnehmer_id):
        session = Session()
        ret = session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)
        if ret.count() != 1:
            return False
        return str(ret.one().unternehmen_mnr)

    def getKursteilnehmerID(self, teilnehmer_id, lehrgang_id):
        session = Session()
        ret = session.query(Kursteilnehmer).filter(
            and_(Kursteilnehmer.teilnehmer_id == teilnehmer_id,
                 Kursteilnehmer.fernlehrgang_id == lehrgang_id))
        if ret.count() != 1:
            return False
        return str(ret.one().id)

    def canLogin(self, teilnehmer_id, passwort):
        session = Session()
        if teilnehmer_id == "admin":
            return False
        ret = session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)
        if ret.count() != 1:
            return False
        ret = ret.one()
        if ret and ret.passwort == passwort:
            return True
        return False

    def changePW(self, teilnehmer_id, passwort):
        if teilnehmer_id == "admin":
            return False
        session = Session()
        ret = session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)
        if ret.count() != 1:
            return False
        ret = ret.one()
        ret.passwort = passwort
        return True 

#
### REST
#

class TeilnehmerAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(ITeilnehmer)

    def GET(self):
        context = self.context
        kt_id = self.request.get('kt', None)
        branche = ""
        un_klasse = ""
        if kt_id:
            for ktn in context.kursteilnehmer: 
                if ktn.id == int(kt_id):
                    branche = ktn.branche
                    un_klasse = ktn.un_klasse
        geburtsdatum = ""
        if context.geburtsdatum:
            geburtsdatum = context.geburtsdatum.strftime('%d.%m.%Y')
        teilnehmer = dict(
            anrede = context.anrede,
            titel = context.titel,
            vorname = context.vorname,
            name = context.name,
            geburtsdatum = geburtsdatum,
            strasse = context.strasse,
            nr = context.nr,
            plz = context.plz,
            ort = context.ort,
            email = context.email,
            un_klasse = un_klasse,
            branche = branche,
            kompetenzzentrum = context.kompetenzzentrum,
            )
        return json.dumps(teilnehmer)


    def PUT(self):
        teilnehmer = self.context
        data = json.loads(self.body)
        un_klasse = data.pop('un_klasse')
        branche = data.pop('branche')
        flg_id = data.pop('flg_id')
        data['geburtsdatum'] = datetime.datetime.strptime(data['geburtsdatum'], "%d.%m.%Y")
        for key, value in data.items():
            if value:
                setattr(teilnehmer, key, value)

        for ktm in teilnehmer.kursteilnehmer:
            if ktm.fernlehrgang_id == int(flg_id):
                ktm.un_klasse = un_klasse
                ktm.branche = branche
                ktm.status = "A1"
        return "1"


class KPTZTeilnehmerAPI(grok.REST):
    grok.layer(KPTZLayer)
    grok.context(ITeilnehmer)

    def PUT(self):
        teilnehmer = self.context
        data = json.loads(self.body[1:-1])
        #data = json.loads(self.body)
        kptz = data.get('kompetenzzentrum')
        teilnehmer.kompetenzzentrum = kptz
        return "1"


class KursteilnehmerAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(IKursteilnehmer)

    def GET(self):
        adapter = ICalculateResults(self.context)
        li = [adapter.summary(), adapter.lehrhefte()]
        return json.dumps(li)


    def PUT(self):
        kursteilnehmer = self.context
        data = json.loads(self.body)
        data['datum'] = datetime.datetime.strptime(data['datum'], "%d.%m.%Y").date()
        data['lehrheft_id'] = int(data['lehrheft_id'])
        data['frage_id'] = int(data['frage_id'])
        antwort = Antwort(**data)
        kursteilnehmer.antworten.append(antwort)
        return antwort.id 
