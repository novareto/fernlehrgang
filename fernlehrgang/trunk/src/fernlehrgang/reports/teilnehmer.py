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
from fernlehrgang.ui_components.viewlets import AboveContent
from fernlehrgang.models import Unternehmen, Kursteilnehmer, Teilnehmer
from zope.interface import Interface

grok.templatedir('templates')

@menuentry(AboveContent, title=u"Unternehmen Suche", order=30)
class UnternehmenSuche(FormTablePage, grok.View):
    grok.context(IFernlehrgangApp)
    ignoreContext = True
    results = []

    fields = Fields(IUnternehmen).select('name')

    @button.buttonAndHandler(u'Suchen')
    def handle_search(self, action):
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Kursteilnehmer, Teilnehmer, Unternehmen)
        sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        sql = sql.filter(Teilnehmer.unternehmen_mnr == Unternehmen.mnr)
        sql = sql.filter(Teilnehmer.unternehmen_mnr == data.get('name'))
        self.results = sql.all()

    @property
    def values(self):
        rc = []
        for kursteilnehmer, teilnehmer, unternehmen in self.results:
            rc.append(dict(flg=kursteilnehmer.fernlehrgang.jahr))
        return rc

    @property
    def displaytable(self):
        self.update()
        return self.renderTable()

class ColumnFernlehrgang(Column):
    grok.name('columnfernlehrgang')
    grok.context(Interface)
    header = "Fernlehrgang"

    def renderCell(self, item):
        return item[fernlehrgang] 
