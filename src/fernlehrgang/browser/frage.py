# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from fernlehrgang.utils import Page
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Frage 
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.frage import IFrage
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang

from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields, button, extends
from z3c.saconfig import Session


from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3ctable.ftests import Container, Content


grok.templatedir('templates')

class AddMenu(MenuItem):
    grok.context(ILehrheft)
    grok.name(u'Resultset verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "frage_view"
    viewURL = "frage_view"

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
        return self.url(self.context, 'frage_view')


class Index(PageDisplayForm, grok.View):
    grok.context(IFrage)

    fields = Fields(IFrage).omit('id')

class FrageView(DeleteFormTablePage, grok.View):
    grok.context(ILehrheft)
    grok.name('frage_view')
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
        self.nextURL = self.url(self.context, 'frage_view')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Frage anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addfrage')) 


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

