# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from uvc.layout.interfaces import ISidebar, IExtraInfo
from fernlehrgang.models import Kursteilnehmer 
from zope.traversing.browser import absoluteURL
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.flg import IFernlehrgang
from megrok.z3cform.tabular import DeleteFormTablePage
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
from zope.cachedescriptors import property

grok.templatedir('templates')


@menuentry(NavigationMenu)
class KursteilnehmerListing(DeleteFormTablePage):
    grok.context(IFernlehrgang)
    grok.name('kursteilnehmer_listing')
    grok.title("Kursteilnehmer verwalten")
    grok.order(10)

    template = grok.PageTemplateFile('templates/base_listing.pt')
    extends(DeleteFormTablePage)
    
    title = u"Kursteilnehmer"
    description = u"Hier können Sie die Kursteilnehmer zu Ihrem Fernlehrgang bearbeiten."

    cssClasses = {'table': 'tablesorter myTable'}

    status = None

    @property.CachedProperty
    def values(self):
        root = getSite()
        for x in self.context.kursteilnehmer:
            locate(root, x, DefaultModel)
        return self.context.kursteilnehmer

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'kursteilnehmer_listing')
        self.request.response.redirect(self.nextURL)

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

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

    def render(self):
        return "<h3>Fernlehrgang: %s - %s </h3>" %(self.context.fernlehrgang.jahr, self.context.fernlehrgang.titel)

## Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgang)
    weight = 0
    cssClasses = {'th': 'checkBox'}
    

class Name(LinkColumn):
    grok.name('Nummer')
    grok.context(IFernlehrgang)
    weight = 10 
    linkContent = "edit"

    def getLinkContent(self, item):
        return "%s %s" % (item.teilnehmer.name, item.teilnehmer.vorname)


class Status(Column):
    grok.name('Status')
    grok.context(IFernlehrgang)
    weight = 20 
    header = u"Status"

    def renderCell(self, item):
        vocab = getUtility(IVocabularyFactory, name='uvc.lieferstopps')(None)
        return vocab.getTerm(item.status).title


class Unternehmen(LinkColumn):
    grok.name('Unternehmen')
    grok.context(IFernlehrgang)
    weight = 99
    linkContent = "index"
    header = "Unternehmen"

    def getLinkContent(self, item):
        return "%s %s" %(item.teilnehmer.unternehmen.mnr, item.teilnehmer.unternehmen.name)

    def getLinkURL(self, item):    
        root = grok.getSite()
        locate(root, item.teilnehmer.unternehmen, DefaultModel)
        return absoluteURL(item.teilnehmer.unternehmen, self.request)
