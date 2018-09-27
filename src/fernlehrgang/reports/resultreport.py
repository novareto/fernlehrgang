# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang import models
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import action, NO_VALUE, Fields
from zope.interface import Interface
from zope.schema import Date 
from fernlehrgang import Form
from profilehooks import profile


grok.templatedir('templates')


class IResultReport(Interface):

    von = Date(
        title = u"Von",
        description = u"Bis",
        required = False,
        )

    bis = Date(
        title = u"Bis",
        description = u"Bis",
        required = False,
        )


#@menuentry(NavigationMenu, order=400)
class ResultReport(Form):
    grok.context(Interface)
    grok.title(u'Ergebnis Nachverfolgung')
    grok.require('zope.View')
    grok.order(20)

    label = u"Ergebnis Nachverfolgung"
    description = u"Bitte geben Sie hier das Start und Ende-Datum Ihrer Suche ein"

    results = []

    fields = Fields(IResultReport)

    def locateit(self, obj):
        site = grok.getSite()
        locate(site, obj, DefaultModel)

    @action(u'Suchen')
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = Session()

        ktns = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == self.context.id,
            models.Antwort.kursteilnehmer_id == models.Kursteilnehmer.id,
            models.Antwort.datum > data['von'] )

        self.results = ktns.all()
