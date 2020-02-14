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
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang import log
from profilehooks import profile


#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


#
### XMLRPC
#

class HelperAPI(grok.XMLRPC):
    grok.context(IFernlehrgangApp)

    def getFlgIds(self, teilnehmer_id):
        #log('getFlgIds %s' % teilnehmer_id, 'performance_analyse')
        session = Session()
        ret = session.query(Kursteilnehmer.fernlehrgang_id).filter(
                Kursteilnehmer.teilnehmer_id == teilnehmer_id,
                Kursteilnehmer.status.in_(('A1', 'A2')))
        return ret.all()

    def getFrageIds(self, lehrheft_id):
        #log('getFrageIds %s' % lehrheft_id, 'performance_analyse')
        session = Session()
        d = dict()
        ret = session.query(Frage).filter(Frage.lehrheft_id==lehrheft_id)
        for frage in ret.all():
            d[frage.frage] = frage.id
        return d

    def getMNRFromTeilnehmerID(self, teilnehmer_id):
        #log('getMNRFromTeilnehmerID %s' % teilnehmer_id, 'performance_analyse')
        session = Session()
        ret = session.query(Teilnehmer.unternehmen_mnr).filter(Teilnehmer.id==teilnehmer_id)
        if ret.count() != 1:
            return False
        return str(ret.one()[0])

    def getKursteilnehmerID(self, teilnehmer_id, lehrgang_id):
        #log('getKursteilnehmerTeilnehmerID %s %s' %(teilnehmer_id, lehrgang_id), 'performance_analyse')
        session = Session()
        ret = session.query(Kursteilnehmer).filter(
            and_(Kursteilnehmer.teilnehmer_id == teilnehmer_id,
                 Kursteilnehmer.fernlehrgang_id == lehrgang_id))
        if ret.count() != 1:
            return False
        return str(ret.one().id)

    def canLogin(self, teilnehmer_id, passwort):
        #log('canLogin %s' %(teilnehmer_id), 'performance_analyse')
        if teilnehmer_id == "admin":
            return 0
        session = Session()
        ret = session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)

        #@timeout_decorator.timeout(8, use_signals=False)
        #def q():
        #    import time
        #    time.sleep(9)
        #    session = Session()
        #    return session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)
        #try:
        #    ret = q()
        #except timeout_decorator.TimeoutError as e:
        #    # log timeout
        #    log('canLogin time out')
        #    return 0
            
        if ret.count() != 1:
            return 0 
        ret = ret.one()
        if ret and ret.passwort == passwort:
            return 1 
        return 0 

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

class UnternehmenAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(IUnternehmen)

    def GET(self):
        #log('UNTERNEHMEN_GET %s ' %(self.context.mnr), 'performance_analyse')
        unternehmen = dict(
            NAME1=self.context.name,
            NAME2=self.context.name2,
            NAME3=self.context.name3,
            STRASSE=self.context.str,
            PLZ=self.context.plz,
            ORT=self.context.ort,)
        return json.dumps(unternehmen)

class TeilnehmerAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(ITeilnehmer)

    def GET(self):
        #log('TEILNEHMER_GET %s ' %(self.context.id), 'performance_analyse')
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
            telefon = context.telefon,
            email = context.email,
            un_klasse = un_klasse,
            branche = branche,
            kompetenzzentrum = context.kompetenzzentrum,
            )
        return json.dumps(teilnehmer)


    def PUT(self):
        #log('TEILNEHMER_PUT %s ' %(self.context.id), 'performance_analyse')
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



from profilehooks import profile
class KursteilnehmerAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(IKursteilnehmer)

    def GET(self):
        #log('KursteilTEILNEHMER_GET %s ' %(self.context.id), 'performance_analyse')
        adapter = ICalculateResults(self.context)
        li = [adapter.summary(), adapter.lehrhefte()]
        return json.dumps(li)


    def PUT(self):
        #log('KursteilTEILNEHMER_PUT %s ' %(self.context.id), 'performance_analyse')
        kursteilnehmer = self.context
        data = json.loads(self.body)
        data['datum'] = datetime.datetime.strptime(data['datum'], "%d.%m.%Y").date()
        data['lehrheft_id'] = int(data['lehrheft_id'])
        data['frage_id'] = int(data['frage_id'])
        antwort = Antwort(**data)
        kursteilnehmer.antworten.append(antwort)
        return antwort.id 
