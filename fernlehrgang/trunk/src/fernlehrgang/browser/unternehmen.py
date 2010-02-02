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
from fernlehrgang.models import Unternehmen 
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.app import IFernlehrgangApp

from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields, button, extends
from z3c.saconfig import Session


from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable import CheckBoxColumn, LinkColumn
from megrok.z3ctable.ftests import Container, Content


grok.templatedir('templates')

class AddMenu(MenuItem):
    grok.context(IFernlehrgangApp)
    grok.name(u'Unternehmen verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "unternehmen"
    viewURL = "unternehmen"

    @property
    def url(self):
        return "%s/%s" % (url(self.request, self.context), self.viewURL)


class AddUnternehmen(PageAddForm, grok.View):
    grok.context(IFernlehrgangApp)
    title = u'Unternehmen'
    label = u'Unternehmen anlegen'

    fields = Fields(IUnternehmen)

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.object = object
        self.context.unternehmen.append(object)

    def nextURL(self):
        return self.url(self.context, 'unternehmen')


class Index(PageDisplayForm, grok.View):
    grok.context(IUnternehmen)

    fields = Fields(IUnternehmen)



class Unternehmen(DeleteFormTablePage, grok.View):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmen_view')
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.unternehmen:
            locate(root, x, DefaultModel)
        return self.context.unternehmen

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'unternehmen')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Unternehmen anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addunternehmen')) 




class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IUnternehmen)
    weight = 0

class Name(LinkColumn):
    grok.name('Nummer')
    grok.context(IUnternehmen)
    weight = 99
    linkContent = "edit"
