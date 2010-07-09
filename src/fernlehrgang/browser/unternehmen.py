# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from dolmen.menu import menuentry
from megrok.traject import locate
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Unternehmen 
from megrok.traject.components import DefaultModel
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.app import IFernlehrgangApp 
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from megrok.z3ctable import Column, CheckBoxColumn, LinkColumn, GetAttrColumn 
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from megrok.z3cform.base.directives import cancellable 
from megrok.z3cform.tabular import FormTablePage


from dolmen.app.layout import IDisplayView, ContextualMenuEntry
from dolmen.app.layout import models
from dolmen.menu import menuentry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from profilehooks import profile



grok.templatedir('templates')

@menuentry(NavigationMenu)
class UnternehmenListing(FormTablePage):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmen_listing')
    grok.title(u"Unternehmen verwalten")
    grok.order(20)

    fields = Fields(IUnternehmen).select('mnr', 'name', 'str', 'plz', 'ort') 

    sortOn = None 

    title = "Unternehmen verwalten"
    description = u"Hier können Sie die Unternehmen der BG-Verwalten"
    ignoreContext = True

    cssClasses = {'table': 'tablesorter myTable'}
    status = None
    results = []

    def updateWidgets(self):
        super(UnternehmenListing, self).updateWidgets()
        for field in self.fields.values():
            field.field.required = False

    #@button.buttonAndHandler(u'Unternehmen anlegen')
    #def handleAddUnternehmen(self, action):
    #     self.redirect(self.url(self.context, 'addunternehmen')) 

    @button.buttonAndHandler(u'Suchen') 
    def handle_search(self, action): 
        rc = [] 
        v=False 
        data, errors = self.extractData() 
        session = Session() 
        sql = session.query(Unternehmen) 
        if data.get('mnr'): 
            sql = sql.filter(Unternehmen.mnr == data.get('mnr')) 
            v = True 
        if data.get('name'): 
            constraint = "%%%s%%" % data.get('name') 
            sql = sql.filter(Unternehmen.name.like(constraint)) 
            v = True 
        if data.get('str'): 
            constraint = "%%%s%%" % data.get('str') 
            sql = sql.filter(Unternehmen.str.like(constraint)) 
            v = True 
        if data.get('plz'): 
            sql = sql.filter(Unternehmen.plz == data.get('plz')) 
            v = True 
        if data.get('ort'): 
            constraint = "%%%s%%" % data.get('ort') 
            sql = sql.filter(Unternehmen.ort.like(constraint)) 
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



class Index(models.DefaultView):
    grok.context(IUnternehmen)
    grok.name('index')
    title = u"Unternehmen"
    label = u"Unternehmen"
    description = u"Details zu Ihrem Unternehmen"

    fields = Fields(IUnternehmen)


@menuentry(AddMenu)
class AddUnternehmen(PageAddForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Unternehmen')
    title = u'Unternehmen'
    label = u'Unternehmen anlegen'
    description = u"Unternehmen anlegen"
    cancellable(True)

    fields = Fields(IUnternehmen)

    def create(self, data):
        return Unternehmen(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        return self.url(self.context, 'unternehmen_listing')



class Mitgliedsnummer(Column):
    grok.name('Mitgliedsnummer')
    grok.context(IFernlehrgangApp)
    weight = 10
    header = u"Mitgliedsnummer"

    def renderCell(self, item):
        locate(grok.getSite(), item, DefaultModel)
        url = grok.url(self.request, item)
        return '<a href="%s"> %s </a>' % (url, item.mnr)

class Name(Column):
    grok.name('Name')
    grok.context(IFernlehrgangApp)
    weight = 20
    header = u"Name"
   
    def renderCell(self, item):
        return item.name 
