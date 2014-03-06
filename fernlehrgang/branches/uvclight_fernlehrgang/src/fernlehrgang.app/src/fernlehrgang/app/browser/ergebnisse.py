# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft, calculations
from sqlalchemy.orm import joinedload
from cromlech.sqlalchemy import get_session

from fernlehrgang.models.calculations import POSTVERSANDSPERRE
from ..interfaces import IKursteilnehmer, ICalculateResults
from .viewlets import NavigationMenu


@menuentry(NavigationMenu)
class Resultate(uvclight.Page):
    uvclight.context(IKursteilnehmer)
    uvclight.title('Ergebnisse')
    uvclight.name('resultate')

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


class CalculateResults(uvclight.Adapter, calculations.KursteilnehmerResults):
    uvclight.context(IKursteilnehmer)

    @staticmethod
    def _lehrhefte(context):
        session = get_session('fernlehrgang')
        sql = session.query(Lehrheft).options(joinedload(Lehrheft.fragen))
        sql = sql.filter(Lehrheft.fernlehrgang_id == context.fernlehrgang.id)
        return sql.all()
