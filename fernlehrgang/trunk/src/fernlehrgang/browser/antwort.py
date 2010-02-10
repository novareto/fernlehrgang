# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.utils import Page
from fernlehrgang.models import Antwort 
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.interfaces.antwort import IAntwort
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.ui_components.viewlets import AboveContent
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends


grok.templatedir('templates')


class AddMenu(MenuItem):
    grok.context(IKursteilnehmer)
    grok.name(u'Antworten verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "antwort_listing"
    viewURL = "antwort_listing"

    @property
    def url(self):
        return "%s/%s" % (url(self.request, self.context), self.viewURL)


class AddAntwort(PageAddForm, grok.View):
    grok.context(IKursteilnehmer)
    title = u'Antwort'
    label = u'Antwort anlegen'

    fields = Fields(IAntwort).omit('id')

    def create(self, data):
        return Antwort(**data)

    def add(self, object):
        self.object = object
        self.context.antworten.append(object)

    def nextURL(self):
        return self.url(self.context, 'antwort_listing')


class Index(PageDisplayForm, grok.View):
    grok.context(IAntwort)
    title = u"Antworten"
    description = u"Hier können Sie Deteils zu Ihren Antworten ansehen."

    fields = Fields(IAntwort).omit('id')


class Edit(PageEditForm, grok.View):
    grok.context(IAntwort)
    grok.name('edit')
    title = u"Antworten"
    description = u"Hier können Sie die Antwort bearbeiten."

    extends(PageEditForm)
    fields = Fields(IAntwort).omit('id')

    @button.buttonAndHandler(u'Fernlehrgang entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 


@menuentry(AboveContent, title=u"Antworten verwalten", order=20)
class AntwortListing(DeleteFormTablePage, grok.View):
    grok.context(IKursteilnehmer)
    grok.name('antwort_listing')
    title = u"Antworten"
    description = u"Hier können Sie die Antworten zu Ihren Lehrheften bearbeiten."
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.antworten:
            locate(root, x, DefaultModel)
        return self.context.antworten

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'antwort_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

    @button.buttonAndHandler(u'Antwort anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addantwort')) 


### Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IKursteilnehmer)
    weight = 0


class Link(LinkColumn):
    grok.name('Nummer')
    grok.context(IKursteilnehmer)
    weight = 5 
    linkContent = "edit"

    def getLinkContent(self, item):
        return "Antwort %s" %item.antwort 


