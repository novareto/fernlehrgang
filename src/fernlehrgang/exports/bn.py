# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import grok

from datetime import datetime
from datetime import timedelta
from zope import interface
from z3c.saconfig import Session
from fernlehrgang import models


JETZT = datetime.now()
T30 = JETZT - timedelta(days=30)
T180 = JETZT - timedelta(days=180)
T300 = JETZT - timedelta(days=300)
T365 = JETZT - timedelta(days=365)


class BN(grok.View):
    grok.context(interface.Interface)

    def update(self):
        session = Session()
        alle_ktns = session.query(models.Kursteilnehmer) #.filter(
            #models.Kursteilnehmer.fernlehrgang_id == models.Fernlehrgang_id,
            #smodels.Fernlehrgang.typ == 'OnlineFortbildung')

        for ktn in alle_ktns.all():
            erstell_datum = ktn.erstell_datum.date()
            print "KTN %s - %s" %(ktn.id, erstell_datum)
            if erstell_datum == T30.date():
                print "30 TAGE"
            elif erstell_datum == T180.date():
                print "180 TAGE"
            elif erstell_datum == T300.date():
                print "300 TAGE"
            elif erstell_datum == T365.date():
                print "356 TAGE"


    def render(self):
        return u"HALLO WELT"
