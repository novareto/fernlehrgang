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


grok.templatedir('templates')

@menuentry(NavigationMenu)
class UnternehmenSuche(FormTablePage):
    grok.context(IFernlehrgangApp)
    grok.title(u'Unternehmen suchen')
    title = label = u"Unternehmen Suchen"
    description = u"Bitte geben Sie das Unternehmen ein, dass Sie suchen möchten"
    ignoreContext = True
    results = []

    fields = Fields(IUnternehmen).select('name')

    @button.buttonAndHandler(u'Suchen')
    def handle_search(self, action):
        rc = []
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Kursteilnehmer, Teilnehmer, Unternehmen)
        sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        sql = sql.filter(Teilnehmer.unternehmen_id == Unternehmen.id)
        sql = sql.filter(Unternehmen.mnr == data.get('name'))
        for kursteilnehmer, teilnehmer, unternehmen in sql.all():
            results = ICalculateResults(kursteilnehmer).summary()
            rc.append(dict(flg = kursteilnehmer.fernlehrgang.jahr,
                           name = teilnehmer.name,
                           vorname = teilnehmer.vorname,
                           id = teilnehmer.id,
                           unternehmen = unternehmen.name,
                           mnr = unternehmen.mnr,
                           bestanden = results['comment'],
                          ))
        self.results = rc

    @property
    def values(self):
        return self.results

    @property
    def displaytable(self):
        self.update()
        return self.renderTable()


class ColumnFernlehrgang(Column):
    grok.name('columnfernlehrgang')
    grok.context(Interface)
    header = "Fernlehrgang"

    def renderCell(self, item):
        return item.get('flg', '-') 


class ColumnTeilnehmer(Column):
    grok.name('columnteilnehmer')
    grok.context(Interface)
    header = "Teilnehmer"

    def renderCell(self, item):
        teilnehmer = "%s, %s" %(item.get('name','-'), item.get('vorname','-'))
        return teilnehmer 


class ColumnUnternehmen(Column):
    grok.name('columnunternehmen')
    grok.context(Interface)
    header = "Unternehmen"

    def renderCell(self, item):
        unternehmen = "%s, %s" % (item.get('mnr','-'), item.get('unternehmen', '-'))
        return unternehmen 


class ColumnResult(Column):
    grok.name('columnresult')
    grok.context(Interface)
    header = "Ergebnis"

    def renderCell(self, item):
        return item['bestanden']
