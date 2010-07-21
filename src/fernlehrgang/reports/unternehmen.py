# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from dolmen.menu import menuentry
from megrok.z3cform.base import PageForm, Fields, button 
from megrok.z3cform.tabular import FormTablePage 
from megrok.z3ctable import Column 
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import Unternehmen, Kursteilnehmer, Teilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
from zope.interface import Interface
from dolmen.app.layout import IDisplayView, ContextualMenuEntry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from dolmen.menu import menuentry
from zope.schema import TextLine
from megrok.traject import locate
from megrok.traject.components import DefaultModel


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
class UnternehmenSuche(FormTablePage):
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage Unternehmen')
    grok.order(20)
    title = label = u"Statusabfrage Unternehmen"
    description = u"Bitte geben Sie Mitgliedsnummer für das Unternehmen ein, dass Sie suchen möchten"
    ignoreContext = True
    results = []

    cssClasses = {'table': 'tablesorter myTable'}
    fields = Fields(IUnternehmenSearch)

    def locateit(self, obj):
        site = grok.getSite()
        locate(site, obj, DefaultModel)

    @button.buttonAndHandler(u'Suchen')
    def handle_search(self, action):
        rc = []
        v = False
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Kursteilnehmer, Teilnehmer, Unternehmen)
        sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        sql = sql.filter(Teilnehmer.unternehmen_mnr == Unternehmen.mnr)
        if data.get('mnr'):
            v = True
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Unternehmen.mnr.like(constraint))
        if data.get('name'):
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

    @property
    def values(self):
        return self.results

    @property
    def displaytable(self):
        self.rows = self.setUpRows()
        return self.renderTable()


class ColumnFernlehrgang(Column):
    grok.name('columnfernlehrgang')
    grok.context(Interface)
    header = "Fernlehrgang"

    def renderCell(self, item):
        return '<a href="%s"> %s </a>' % (item.get('link_flg'), item.get('flg', '-')) 


class ColumnTeilnehmer(Column):
    grok.name('columnteilnehmer')
    grok.context(Interface)
    header = "Teilnehmer"

    def renderCell(self, item):
        teilnehmer = "%s, %s" %(item.get('name','-'), item.get('vorname','-'))
        return '<a href="%s"> %s </a>' %(item.get('link_kt'), teilnehmer)


class ColumnUnternehmen(Column):
    grok.name('columnunternehmen')
    grok.context(Interface)
    header = "Unternehmen"

    def renderCell(self, item):
        unternehmen = "%s, %s" % (item.get('mnr','-'), item.get('unternehmen', '-'))
        return '<a href="%s"> %s </a>' %(item.get('link_unternehmen'), unternehmen) 


class ColumnResult(Column):
    grok.name('columnresult')
    grok.context(Interface)
    header = "Ergebnis"

    def renderCell(self, item):
        return '<a href="%s/resultate"> %s </a>' % (item.get('link_kt'), item['bestanden'])
