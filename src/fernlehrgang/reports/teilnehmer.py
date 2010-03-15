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
from megrok.z3ctable import Column 
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.models import Teilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
from zope.interface import Interface
from dolmen.app.layout import IDisplayView, ContextualMenuEntry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from dolmen.menu import menuentry


grok.templatedir('templates')

@menuentry(NavigationMenu)
class TeilnehmerSuche(PageForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Teilnehmer suchen')
    grok.require('uvc.manageteilnehmer')
    title = label = u"Teilnehmer suchen"
    description = u"Bitte geben Sie den Teilnehmer ein, den Sie suchen möchten"
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
        teilnehmer = sql.first()
        if teilnehmer:
            site = grok.getSite()
            locate(site, teilnehmer, DefaultModel)
            self.redirect(self.url(teilnehmer, 'edit'))
        else:    
            self.flash('Es wurde kein Teilnehmer gefunden')
