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
from fernlehrgang.models import Lehrheft 
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang

from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields, button, extends
from z3c.saconfig import Session


from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable import CheckBoxColumn, LinkColumn
from megrok.z3ctable.ftests import Container, Content


grok.templatedir('templates')

class AddMenu(MenuItem):
    grok.context(IFernlehrgang)
    grok.name(u'Lehrhefte verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "lehrhefte"
    viewURL = "lehrhefte"

    @property
    def url(self):
        return "%s/%s" % (url(self.request, self.context), self.viewURL)


class AddLehrheft(PageAddForm, grok.View):
    grok.context(IFernlehrgang)
    title = u'Lehrheft'
    label = u'Lehrheft anlegen'

    fields = Fields(ILehrheft).omit('id')

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.object = object
        self.context.lehrhefte.append(object)

    def nextURL(self):
        return self.url(self.context, 'lehrhefte')


class Index(PageDisplayForm, grok.View):
    grok.context(ILehrheft)

    fields = Fields(ILehrheft).omit(id)



class Lehrhefte(DeleteFormTablePage, grok.View):
    grok.context(IFernlehrgang)
    grok.name('lehrhefte')
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.lehrhefte:
            locate(root, x, DefaultModel)
        return self.context.lehrhefte

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'lehrhefte')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Lehrheft anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addlehrheft')) 




class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgang)
    weight = 0

class Name(LinkColumn):
    grok.name('Nummer')
    grok.context(IFernlehrgang)
    weight = 99
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.titel
