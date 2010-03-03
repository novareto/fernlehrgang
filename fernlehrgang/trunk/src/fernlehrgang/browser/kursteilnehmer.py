# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.utils import Page
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Kursteilnehmer 
from zope.traversing.browser import absoluteURL
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.flg import IFernlehrgang
from megrok.z3ctable.ftests import Container, Content
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends

from dolmen.menu import menuentry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from dolmen.app.layout import IDisplayView, ContextualMenuEntry

grok.templatedir('templates')

@menuentry(NavigationMenu)
class KursteilnehmerListing(DeleteFormTablePage, ContextualMenuEntry):
    grok.context(IFernlehrgang)
    grok.name('kursteilnehmer_listing')
    grok.title("Kursteilnehmer verwalten")
    grok.order(10)
    
    title = u"Kursteilnehmer"
    description = u"Hier können Sie die Kursteilnehmer zu Ihrem Fernlehrgang bearbeiten."
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.kursteilnehmer:
            locate(root, x, DefaultModel)
        return self.context.kursteilnehmer

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'kursteilnehmer_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Kursteilnehmer anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addkursteilnehmer')) 

@menuentry(AddMenu)
class AddKursteilnehmer(PageAddForm):
    grok.context(IFernlehrgang)
    grok.title(u'Kursteilnehmer anlegen')
    title = u'Kursteilnehmer'
    label = u'Kursteilnehmer anlegen'
    description = u'Kursteilnehmer anlegen'

    fields = Fields(IKursteilnehmer).omit('id')

    def create(self, data):
        return Kursteilnehmer(**data)

    def add(self, object):
        self.object = object
        self.context.kursteilnehmer.append(object)

    def nextURL(self):
        return self.url(self.context, 'kursteilnehmer_listing')


class Index(PageDisplayForm, ContextualMenuEntry):
    grok.context(IKursteilnehmer)
    grok.implements(IDisplayView)
    grok.title(u'View')
    title = u"Unternehmen"
    description = u"Details zu Ihrem Unternehmen"

    fields = Fields(IKursteilnehmer).omit(id)


class Edit(PageEditForm, ContextualMenuEntry):
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


class Status(GetAttrColumn):
    grok.name('Status')
    grok.context(IFernlehrgang)
    weight = 20 
    header = u"Status"
    attrName = "status"


class Unternehmen(LinkColumn):
    grok.name('Unternehmen')
    grok.context(IFernlehrgang)
    weight = 99
    linkContent = "index"
    header = "Unternehmen"

    def getLinkContent(self, item):
        return item.teilnehmer.unternehmen.name

    def getLinkURL(self, item):    
        root = grok.getSite()
        locate(root, item.teilnehmer.unternehmen, DefaultModel)
        return absoluteURL(item.teilnehmer.unternehmen, self.request)
