# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft, calculations
from megrok.layout import Page
from sqlalchemy.orm import joinedload
from z3c.saconfig import Session

from ..config import POSTVERSANDSPERRE
from ..interfaces import IKursteilnehmer, ICalculateResults
from .viewlets import NavigationMenu


grok.templatedir('templates')


@menuentry(NavigationMenu)
class Resultate(Page):
    grok.context(IKursteilnehmer)
    grok.title('Ergebnisse')
    grok.name('resultate')

    title = u"Resultate"

    @property
    def description(self):
        teilnehmer = self.context.teilnehmer
        return u"Hier Können Sie die Resultate des Kursteilnehmers %s %s KTID %s einsehen." % (
                teilnehmer.name, teilnehmer.vorname, self.context.id)

    @property
    def getResults(self):
        results = ICalculateResults(self.context)
        return results.lehrhefte()

    @property
    def getSummary(self):
        results = ICalculateResults(self.context)
        return results.summary()


def checkDate(date):
    if date:
        return date.strftime('%d.%m.%Y %H:%M')
    else:
        return ""


class CalculateResults(grok.Adapter, calculations.KursteilnehmerResults):
    grok.context(IKursteilnehmer)

    @staticmethod
    def _lehrhefte(context):
        session = Session()
        sql = session.query(Lehrheft).options(joinedload(Lehrheft.fragen))
        sql = sql.filter(Lehrheft.fernlehrgang_id == context.fernlehrgang.id)
        return sql.all()
