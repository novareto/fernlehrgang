# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from uvc.layout.interfaces import ISidebar, IExtraInfo
from fernlehrgang.models import Kursteilnehmer, Teilnehmer 
from zope.traversing.browser import absoluteURL
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from megrok.z3cform.tabular import FormTablePage
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn, Column, TablePage
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from megrok.z3cform.base.directives import cancellable

from dolmen.menu import menuentry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from dolmen.app.layout import models, ContextualMenuEntry
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from profilehooks import profile
from sqlalchemy import and_
from zope.cachedescriptors.property import CachedProperty

grok.templatedir('templates')


@menuentry(NavigationMenu)
class KursteilnehmerListing(FormTablePage):
    grok.context(IFernlehrgang)
    grok.name('kursteilnehmer_listing')
    grok.title("Kursteilnehmer verwalten")
    grok.order(10)
    ignoreContext = True
    template = grok.PageTemplateFile('templates/base_listing.pt')
    fields = Fields(IKursteilnehmer).select('id') + Fields(ITeilnehmer).select('name', 'geburtsdatum')
    fields['id'].field.readonly = False


    title = u"Kursteilnehmer"
    description = u"Hier können Sie die Kursteilnehmer zu Ihrem Fernlehrgang bearbeiten."

    cssClasses = {'table': 'tablesorter myTable'}

    status = None
    results = []

    def updateWidgets(self):
        super(KursteilnehmerListing, self).updateWidgets()
        for field in self.fields.values():
            field.field.required = False

    @button.buttonAndHandler(u'Suchen') 
    def handle_search(self, action): 
        rc = [] 
        v=False 
        data, errors = self.extractData() 
        session = Session() 
        flg_id = self.context.id
        sql = session.query(Teilnehmer, Kursteilnehmer)
        sql = sql.filter(and_(Kursteilnehmer.fernlehrgang_id == flg_id, Kursteilnehmer.teilnehmer_id == Teilnehmer.id)) 
        if data.get('id'): 
            sql = sql.filter(Kursteilnehmer.id == data.get('id')) 
            v = True 
        if data.get('name'): 
            qu = "%%%s%%" % data.get('name')
            sql = sql.filter(Teilnehmer.name.like(qu)) 
            v = True 
        if data.get('geburtsdatum'): 
            sql = sql.filter(Teilnehmer.geburtsdatum == data.get('geburtsdatum')) 
            v = True 
        if not v: 
            self.flash(u'Bitte geben Sie Suchkriterien ein.') 
            return 
        print sql    
        self.results = sql.all()

    @property    
    def values(self):
        return self.results

    @CachedProperty
    def displaytable(self):
        self.update()
        return self.renderTable()

    @button.buttonAndHandler(u'Kursteilnehmer anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addkursteilnehmer')) 


@menuentry(AddMenu)
class AddKursteilnehmer(PageAddForm):
    grok.context(IFernlehrgang)
    grok.title(u'Kursteilnehmer')
    title = u'Kursteilnehmer'
    label = u'Kursteilnehmer anlegen'
    description = u'Kursteilnehmer anlegen'
    cancellable(True)

    fields = Fields(IKursteilnehmer).omit('id')

    def create(self, data):
        return Kursteilnehmer(**data)

    def add(self, object):
        self.object = object
        self.context.kursteilnehmer.append(object)

    def nextURL(self):
        self.flash(u'Der Kursteilnehmer wurde erfolgreich angemeldet')
        return self.url(self.context, 'kursteilnehmer_listing')


class Index(models.DefaultView):
    grok.context(IKursteilnehmer)
    grok.title(u'View')
    title = label = u"Kursteilnehmer"
    description = u"Details zum Kursteilnehmer"

    fields = Fields(IKursteilnehmer).omit(id)


class Edit(models.Edit):
    grok.context(IKursteilnehmer)
    grok.name('edit')
    grok.title(u'Edit')
    extends(PageEditForm)

    fields = Fields(IKursteilnehmer).omit('id')

    @button.buttonAndHandler(u'Kursteilnehmer entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 


# More Info Viewlets

class MoreInfoKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IFernlehrgang) 

    def render(self):
        return "<h3>Fernlehrgang %s - %s </h3>" %(self.context.jahr, self.context.titel)

class MoreInfoOnKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IKursteilnehmer)
    script = ""

    def update(self):
        url = grok.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url

    def render(self):
        return "%s <h3>Fernlehrgang: %s - %s </h3>" %(self.script, 
            self.context.fernlehrgang.jahr, self.context.fernlehrgang.titel)

## Spalten


class Name(Column):
    grok.name('Nummer')
    grok.context(IFernlehrgang)
    weight = 10 
    header = "Kursteilnehmer"

    def renderCell(self, item):
        teilnehmer, kursteilnehmer = item
        root = grok.getSite()
        locate(root, kursteilnehmer, DefaultModel)
        url = absoluteURL(kursteilnehmer, self.request)
        name = "%s %s" %(teilnehmer.name, teilnehmer.vorname)
        return '<a href="%s"> %s </a>' %(url, name)


class Status(Column):
    grok.name('Status')
    grok.context(IFernlehrgang)
    weight = 20 
    header = u"Status"

    def renderCell(self, item):
        teilnehmer, kursteilnehmer = item
        vocab = getUtility(IVocabularyFactory, name='uvc.lieferstopps')(None)
        return vocab.getTerm(kursteilnehmer.status).title


class Unternehmen(Column):
    grok.name('Unternehmen')
    grok.context(IFernlehrgang)
    weight = 99
    linkContent = "index"
    header = "Unternehmen"

    def renderCell(self, item):
        teilnehmer, kursteilnehmer = item
        root = grok.getSite()
        locate(root, teilnehmer.unternehmen, DefaultModel)
        url = absoluteURL(teilnehmer.unternehmen, self.request)
        name = "%s %s" %(teilnehmer.unternehmen.mnr, teilnehmer.unternehmen.name)
        return '<a href="%s"> %s </a>' %(url, name)
