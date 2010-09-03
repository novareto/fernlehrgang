# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import json

from z3c.saconfig import Session
from fernlehrgang.models import Teilnehmer, Antwort
from fernlehrgang.app import RestLayer
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer


#
### XMLRPC
#

class HelperAPI(grok.XMLRPC):
    grok.context(IFernlehrgangApp)

    def getMNRFromTeilnehmerID(self, teilnehmer_id):
        session = Session()
        ret = session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)
        if ret.count != 1:
            return False
        return str(ret.one().unternehmen_mnr)

    def canLogin(self, teilnehmer_id, passwort):
        session = Session()
        ret = session.query(Teilnehmer).filter(Teilnehmer.id==teilnehmer_id)
        if ret.count != 1:
            return False
        ret = ret.one()
        if ret and ret.passwort == passwort:
            return True
        return False

#
### REST
#

class TeilnehmerAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(ITeilnehmer)

    def GET(self):
        print "GEHT"
        return "GEHT"

    def PUT(self):
        teilnehmer = self.context
        data = json.loads(self.body)
        for key, value in data.items():
            if value:
                setattr(teilnehmer, key, value)
        return "1"


class KursteilnehmerAPI(grok.REST):
    grok.layer(RestLayer)
    grok.context(IKursteilnehmer)

    def PUT(self):
        kursteilnehmer = self.context
        data = json.loads(self.body)
        antwort = Antwort(**data)
        kursteilnehmer.antworten.append(antwort)
