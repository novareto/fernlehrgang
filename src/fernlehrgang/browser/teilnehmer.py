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
from fernlehrgang.models import Teilnehmer 
from uvc.layout.interfaces import ISidebar
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.ui_components.viewlets import AboveContent
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends


grok.templatedir('templates')


class AddMenu(MenuItem):
    grok.context(IUnternehmen)
    grok.name(u'Teilnehmer verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "teilnehmer_listing"
    viewURL = "teilnehmer_listing"

    @property
    def url(self):
        return "%s/%s" % (url(self.request, self.context), self.viewURL)


@menuentry(AboveContent, title="Teilnehmer verwalten", order=10)
class TeilnehmerListing(DeleteFormTablePage, grok.View):
    grok.context(IUnternehmen)
    grok.name('teilnehmer_listing')
    title = u"Teilnehmer"
    description = u"Hier können Sie die Teilnehmer zu Ihrem Fernlehrgang bearbeiten."
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.teilnehmer:
            locate(root, x, DefaultModel)
        return self.context.teilnehmer

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'teilnehmer_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Teilnehmer anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addteilnehmer')) 


class AddTeilnehmer(PageAddForm, grok.View):
    grok.context(IUnternehmen)
    title = u'Teilnehmer'
    label = u'Teilnehmer anlegen'

    fields = Fields(ITeilnehmer).omit('id')

    def create(self, data):
        return Teilnehmer(**data)

    def add(self, object):
        self.object = object
        self.context.teilnehmer.append(object)

    def nextURL(self):
        return self.url(self.context, 'teilnehmer_listing')


class Index(PageDisplayForm, grok.View):
    grok.context(ITeilnehmer)
    title = u"Unternehmen"
    description = u"Details zu Ihrem Unternehmen"

    fields = Fields(ITeilnehmer).omit(id)


class Edit(PageEditForm, grok.View):
    grok.context(ITeilnehmer)
    grok.name('edit')
    extends(PageEditForm)

    fields = Fields(ITeilnehmer).omit('id')

    @button.buttonAndHandler(u'Teilnehmer entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 

## Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IUnternehmen)
    weight = 0
    cssClasses = {'th': 'checkBox'}
    

class Name(LinkColumn):
    grok.name('Name')
    grok.context(IUnternehmen)
    weight = 10 
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.name


class VorName(GetAttrColumn):
    grok.name('VorName')
    grok.context(IUnternehmen)
    weight = 20 
    header = u"Vorname"
    attrName = "vorname"

class Geburtsdatum(GetAttrColumn):    
    grok.name('Geburtsdatum')
    grok.context(IUnternehmen)
    weight = 30 
    header = u"Geburtsdatum"
    attrName = "geburtsdatum"