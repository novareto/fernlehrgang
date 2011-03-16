# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
import uvc.layout

from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import Teilnehmer
from fernlehrgang.ui_components import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import action, NO_VALUE, Fields


grok.templatedir('templates')


@menuentry(NavigationMenu, order=500)
class CreateTeilnehmer(uvc.layout.Form):
    grok.context(IFernlehrgangApp)
    grok.title(u'Teilnehmer registrieren')
    grok.require('uvc.manageteilnehmer')
    title = label = u"Teilnehmer registrieren"
    description = u"Bitte geben Sie die Teilnehmer ID ein, den Sie registrieren möchten."
    results = []

    cssClasses = {'table': 'tablesorter myTable'}

    fields = Fields(ITeilnehmer).select('id')
    fields['id'].readonly = False

    @action(u'Suchen')
    def handle_search(self):
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Teilnehmer)
        sql = sql.filter(Teilnehmer.id == data.get('id'))
        teilnehmer = sql.first()
        if teilnehmer:
            site = grok.getSite()
            locate(site, teilnehmer, DefaultModel)
            self.redirect(self.url(teilnehmer, 'edit'))
        else:
            self.flash('Es wurde kein Teilnehmer gefunden')


@menuentry(NavigationMenu, order=450)
class TeilnehmerSuche(uvc.layout.Form):
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage Teilnehmer')
    grok.require('uvc.manageteilnehmer')
    grok.order(1500)

    label = u"Statusabfrage Teilnehmer."
    description = u"Bitte geben Sie die Kriterien ein um den Teilnehmer zu finden."

    fields = Fields(ITeilnehmer).select('id', 'name') + Fields(IUnternehmen).select('mnr')
    fields['id'].readonly = False
    fields['mnr'].readonly = False
    fields['name'].required = False

    results = []

    def getResults(self):
        root = grok.getSite()
        for item in self.results:
            locate(root, item, DefaultModel)
            locate(root, item.unternehmen, DefaultModel)
            name = '<a href="%s"> %s </a>' % (self.url(item), item.name)
            unternehmen = '<a href="%s"> %s </a>' % (self.url(item.unternehmen), item.unternehmen.name)
            d = dict(name=name,
                     vorname=item.vorname,
                     gebdat=item.geburtsdatum.strftime('%d.%m.%Y'),
                     unternehmen=unternehmen)
            yield d

    @action(u'Suchen')
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Teilnehmer)
        if data.get('id') != NO_VALUE:
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if data.get('name') != NO_VALUE:
            constraint = "%%%s%%" % data.get('name')
            sql = sql.filter(Teilnehmer.name.like(constraint))
            v = True
        if data.get('mnr') != NO_VALUE:
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Teilnehmer.unternehmen_mnr.like(constraint))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()
