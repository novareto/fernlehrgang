# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from fernlehrgang.app.interfaces import IFernlehrgangApp
from fernlehrgang.models import ICalculateResults
from fernlehrgang.models import Unternehmen, Kursteilnehmer, Teilnehmer
from fernlehrgang.app.browser.viewlets import NavigationMenu
from zope.interface import Interface
from zope.schema import TextLine
from cromlech.sqlalchemy import get_session
from uvclight.backends.patterns import DefaultModel
from fernlehrgang.app.wsgi import model_lookup


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


@uvclight.menuentry(NavigationMenu, order=400)
class UnternehmenSuche(uvclight.Form):
    uvclight.context(IFernlehrgangApp)
    uvclight.title(u'Statusabfrage Unternehmen')
    uvclight.require('zope.View')
    uvclight.order(20)

    label = u"Statusabfrage Unternehmen"
    description = u"Bitte geben Sie Mitgliedsnummer für das Unternehmen ein, dass Sie suchen möchten"

    results = []

    fields = uvclight.Fields(IUnternehmenSearch)

    def locateit(self, obj):
        site = grok.getSite()
        model_lookup.patterns.locate(site, obj, DefaultModel)

    @uvclight.action(u'Suchen')
    def handle_search(self):
        rc = []
        v = False
        data, errors = self.extractData()
        session = get_session('fernlehrgang') 
        sql = session.query(Kursteilnehmer, Teilnehmer, Unternehmen)
        sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        sql = sql.filter(Teilnehmer.unternehmen_mnr == Unternehmen.mnr)
        if data.get('mnr') != "":
            v = True
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Unternehmen.mnr.like(constraint))
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
