# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang.models import Unternehmen, Kursteilnehmer, Teilnehmer
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import action, NO_VALUE, Fields
from zope.interface import Interface
from zope.schema import TextLine
from fernlehrgang import Form


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

    mnr_g_alt = TextLine(
        title = u"Mitgliedsnummer G Alt",
        description = u"Alte Mitgliedsnummer der Sparte G",
        required = False,
        )


@menuentry(NavigationMenu, order=400)
class UnternehmenSuche(Form):
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage Unternehmen')
    grok.require('zope.View')
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
        sql = session.query(Unternehmen)
        #sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        #sql = sql.filter(Teilnehmer.unternehmen_mnr == Unternehmen.mnr)
        if data.get('mnr') != "":
            v = True
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Unternehmen.mnr == data.get('mnr'))
        if data.get('mnr_g_alt') != "":
            v = True
            constraint = "%%%s%%" % data.get('mnr_g_alt')
            sql = sql.filter(Unternehmen.mnr_g_alt.like(constraint))
        if data.get('name') != "":
            v = True
            constraint = "%%%s%%" % data.get('name')
            sql = sql.filter(Unternehmen.name.ilike(constraint))
        if not v:
            self.flash(u'Bitte geben Sie entsprechende Kriterien ein.')
            return
        for unternehmen in sql.all():
            for teilnehmer in unternehmen.teilnehmer:
                for kursteilnehmer in teilnehmer.kursteilnehmer:
                    results = ICalculateResults(kursteilnehmer).summary(unternehmen=unternehmen)
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
