# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang.models import Unternehmen, Kursteilnehmer, Teilnehmer
from fernlehrgang.ui_components import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import action, NO_VALUE, Fields
from zope.interface import Interface
from zope.schema import TextLine


grok.templatedir('templates')


class IUnternehmenSearch(Interface):

    mnr = TextLine(
        title = u"Mitgliedsnummer",
        description = u"Mitgliedsnummer des Unternehmens",
        required = False,
        )

    name = TextLine(
        title = u"Name",
        description = u"Name des Unternehmens",
        required = False,
        )


@menuentry(NavigationMenu, order=400)
class UnternehmenSuche(uvc.layout.Form):
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage Unternehmen')
    grok.order(20)

    label = u"Statusabfrage Unternehmen"
    description = u"Bitte geben Sie Mitgliedsnummer für das Unternehmen ein, dass Sie suchen möchten"

    results = []

    fields = Fields(IUnternehmenSearch)

    def locateit(self, obj):
        site = grok.getSite()
        locate(site, obj, DefaultModel)

    @action(u'Suchen')
    def handle_search(self):
        rc = []
        v = False
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Kursteilnehmer, Teilnehmer, Unternehmen)
        sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        sql = sql.filter(Teilnehmer.unternehmen_mnr == Unternehmen.mnr)
        if data.get('mnr') != NO_VALUE:
            v = True
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Unternehmen.mnr.like(constraint))
        if data.get('name') != NO_VALUE:
            v = True
            constraint = "%%%s%%" % data.get('name')
            sql = sql.filter(Unternehmen.name.like(constraint))
        if not v:
            self.flash(u'Bitte geben Sie entsprechende Kriterien ein.')
            return
        for kursteilnehmer, teilnehmer, unternehmen in sql.all():
            results = ICalculateResults(kursteilnehmer).summary()
            flg = kursteilnehmer.fernlehrgang
            self.locateit(flg)
            self.locateit(unternehmen)
            self.locateit(kursteilnehmer)
            link_flg = self.url(flg)
            link_unternehmen = self.url(unternehmen)
            link_kursteilnehmer = self.url(kursteilnehmer)
            rc.append(dict(flg = kursteilnehmer.fernlehrgang.jahr + ' ' + kursteilnehmer.fernlehrgang.titel,
                           link_flg = link_flg,
                           name = teilnehmer.name,
                           vorname = teilnehmer.vorname,
                           link_kt = link_kursteilnehmer,
                           id = teilnehmer.id,
                           unternehmen = unternehmen.name,
                           link_unternehmen = link_unternehmen,
                           mnr = unternehmen.mnr,
                           bestanden = results['comment'],
                          ))
        self.results = rc
