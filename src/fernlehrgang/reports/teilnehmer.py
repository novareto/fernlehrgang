# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from dolmen.menu import menuentry
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3cform.base import PageForm, Fields, button 
from megrok.z3cform.tabular import FormTablePage 
from megrok.z3ctable import Column, GetAttrColumn 
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import Teilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
from zope.interface import Interface
from dolmen.app.layout import IDisplayView, ContextualMenuEntry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from dolmen.menu import menuentry


grok.templatedir('templates')

@menuentry(NavigationMenu, order=500)
class CreateTeilnehmer(PageForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Teilnehmer registrieren')
    grok.require('uvc.manageteilnehmer')
    title = label = u"Teilnehmer registrieren"
    description = u"Bitte geben Sie die Teilnehmer ID ein, den Sie registrieren möchten."
    ignoreContext = True
    results = []

    cssClasses = {'table': 'tablesorter myTable'}
    fields = Fields(ITeilnehmer).select('id')
    fields['id'].field.readonly = False

    @button.buttonAndHandler(u'Suchen')
    def handle_search(self, action):
        rc = []
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Teilnehmer)
        sql = sql.filter(Teilnehmer.id == data.get('id'))
        print sql
        teilnehmer = sql.first()
        if teilnehmer:
            site = grok.getSite()
            locate(site, teilnehmer, DefaultModel)
            self.redirect(self.url(teilnehmer, 'edit'))
        else:    
            self.flash('Es wurde kein Teilnehmer gefunden')


@menuentry(NavigationMenu, order=450)
class TeilnehmerSuche(FormTablePage):
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage Teilnehmer')
    grok.require('uvc.manageteilnehmer')
    grok.order(1500)
    title = label = u"Statusabfrage Teilnehmer."
    description = u"Bitte geben Sie die Kriterien ein um den Teilnehmer zu finden."
    ignoreContext = True
    results = []

    cssClasses = {'table': 'tablesorter myTable'}
    fields = Fields(ITeilnehmer).select('id', 'name') + Fields(IUnternehmen).select('mnr')
    fields['id'].field.readonly = False
    fields['mnr'].field.readonly = False
    fields['name'].field.required = False

    @button.buttonAndHandler(u'Suchen')
    def handle_search(self, action):
        rc = []
        v=False
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Teilnehmer)
        if data.get('id'):
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if data.get('name'):
            constraint = "%%%s%%" % data.get('name')
            sql = sql.filter(Teilnehmer.name.like(constraint))
            v = True
        if data.get('mnr'):
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Teilnehmer.unternehmen_mnr.like(constraint))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()

    @property
    def values(self):
        return self.results

    @property
    def displaytable(self):
        self.update()
        return self.renderTable()


class ColumnName(Column):
    grok.name('teilnehmername')
    grok.context(Interface)
    header = "Name"

    def renderCell(self, item):
        locate(grok.getSite(), item, DefaultModel)
        url = grok.url(self.request, item)
        return '<a href="%s"> %s </a>' % (url, item.name)


class ColumnVorName(GetAttrColumn):
    grok.name('teilnehmervorname')
    grok.context(Interface)
    header = "Vorname"
    attrName = "vorname"


class ColumnGebDat(Column):
    grok.name('teilnehmergebdat')
    grok.context(Interface)
    header = "Geburtsdatum"

    def renderCell(self, item):
        return item.geburtsdatum.strftime('%d.%m.%Y')


class ColumnMNR(Column):
    grok.name('teilnehmermnr')
    grok.context(Interface)
    header = "Unternehmen"

    def renderCell(self, item):
        locate(grok.getSite(), item.unternehmen, DefaultModel)
        url = grok.url(self.request, item.unternehmen)
        return '<a href="%s"> %s </a>' % (url, item.unternehmen.name)
