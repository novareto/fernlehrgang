# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
import uvc.layout

from dolmen.app.layout import models
from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp 
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import Unternehmen 
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import NO_VALUE
from zeam.form.base import action


grok.templatedir('templates')

@menuentry(NavigationMenu)
class UnternehmenListing(uvc.layout.Form):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmen_listing')
    grok.title(u"Unternehmen verwalten")
    grok.order(20)
    
    fields = Fields(IUnternehmen).select('mnr', 'name', 'str', 'plz', 'ort')

    label = u"Unternehmen verwalten"
    description = u"Hier können Sie die am Fernlehrgang teilnehmenden Unternehmen verwalten"

    results = []

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    def getResults(self):
        for item in self.results:
            locate(grok.getSite(), item, DefaultModel)
            yield item

    @action(u"Suchen")
    def handle_search(self): 
        v=False 
        data, errors = self.extractData() 
        session = Session() 
        sql = session.query(Unternehmen) 
        if data.get('mnr') != NO_VALUE: 
            sql = sql.filter(Unternehmen.mnr == data.get('mnr')) 
            v = True 
        if data.get('name') != NO_VALUE: 
            constraint = "%%%s%%" % data.get('name') 
            sql = sql.filter(Unternehmen.name.ilike(constraint)) 
            v = True 
        if data.get('str') != NO_VALUE: 
            constraint = "%%%s%%" % data.get('str') 
            sql = sql.filter(Unternehmen.str.ilike(constraint)) 
            v = True 
        if data.get('plz') != NO_VALUE: 
            sql = sql.filter(Unternehmen.plz == data.get('plz')) 
            v = True 
        if data.get('ort') != NO_VALUE: 
            constraint = "%%%s%%" % data.get('ort') 
            sql = sql.filter(Unternehmen.ort.ilike(constraint)) 
            v = True 
        if not v: 
            self.flash(u'Bitte geben Sie die Suchkriterien ein.') 
            return 
        self.results = sql.all() 


class Index(models.DefaultView):
    grok.context(IUnternehmen)
    grok.name('index')
    template = grok.PageTemplateFile('templates/unternehmen_view.pt')

    title = u"Unternehmen"
    label = u"Unternehmen"
    description = u"Details zum Unternehmen"

    fields = Fields(IUnternehmen)

    def getTeilnehmerListing(self):
        rc = []
        for teilnehmer in self.context.teilnehmer:
            person = dict(name = "%s %s" %(teilnehmer.name, teilnehmer.vorname),
                          gebdat = teilnehmer.geburtsdatum,
                          lehrgang = [])
            for kursteilnehmer in self.context.kursteilnehmer:
                if teilnehmer.id == kursteilnehmer.teilnehmer.id:
                    if kursteilnehmer.fernlehrgang:
                        person['lehrgang'].append(kursteilnehmer.fernlehrgang.titel)
                    else:
                        person['lehrgang'].append(u'Noch für keinen Fernlehrgang registriert.')
            rc.append(person)
        return rc
