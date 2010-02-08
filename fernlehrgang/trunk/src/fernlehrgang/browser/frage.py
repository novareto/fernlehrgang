# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.utils import Page
from fernlehrgang.models import Frage 
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.interfaces.frage import IFrage
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.ui_components.viewlets import AboveContent
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends


grok.templatedir('templates')


class AddMenu(MenuItem):
    grok.context(ILehrheft)
    grok.name(u'Fragen verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "frage_listing"
    viewURL = "frage_listing"

    @property
    def url(self):
        return "%s/%s" % (url(self.request, self.context), self.viewURL)


class AddFrage(PageAddForm, grok.View):
    grok.context(ILehrheft)
    title = u'Frage'
    label = u'Frage anlegen'

    fields = Fields(IFrage).omit('id')

    def create(self, data):
        return Frage(**data)

    def add(self, object):
        self.object = object
        self.context.fragen.append(object)

    def nextURL(self):
        return self.url(self.context, 'frage_listing')


class Index(PageDisplayForm, grok.View):
    grok.context(IFrage)
    title = u"Fragen"
    description = u"Hier können Sie Deteils zu Ihren Fragen ansehen."

    fields = Fields(IFrage).omit('id')


class Edit(PageEditForm, grok.View):
    grok.context(IFrage)
    grok.name('edit')
    title = u"Fragen"
    description = u"Hier können Sie die Frage bearbeiten."

    extends(PageEditForm)
    fields = Fields(IFrage).omit('id')

    @button.buttonAndHandler(u'Fernlehrgang entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 


@menuentry(AboveContent, title=u"Fragen verwalten", order=20)
class FrageListing(DeleteFormTablePage, grok.View):
    grok.context(ILehrheft)
    grok.name('frage_listing')
    title = u"Fragen"
    description = u"Hier können Sie die Fragen zu Ihren Lehrheften bearbeiten."
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.fragen:
            locate(root, x, DefaultModel)
        return self.context.fragen

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'frage_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

    @button.buttonAndHandler(u'Frage anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addfrage')) 


### Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(ILehrheft)
    weight = 0


class Link(LinkColumn):
    grok.name('Nummer')
    grok.context(ILehrheft)
    weight = 5 
    linkContent = "edit"

    def getLinkContent(self, item):
        return "Frage %s" %item.frage 


class Antwortschema(GetAttrColumn):
    grok.name('Antwortschema')
    grok.context(ILehrheft)
    weight = 10
    attrName = 'antwortschema'
    header = u"Antwortschema"


class Gewichtung(GetAttrColumn):
    grok.name('Gewichtung')
    grok.context(ILehrheft)
    weight = 20
    attrName = 'gewichtung'
    header = u"Gewichtung"

