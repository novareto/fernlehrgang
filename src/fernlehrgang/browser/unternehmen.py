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
from megrok.z3ctable import CheckBoxColumn, LinkColumn, GetAttrColumn 
from megrok.z3ctable.ftests import Container, Content


grok.templatedir('templates')

class AddUnternehmenMenu(MenuItem):
    grok.context(IFernlehrgangApp)
    grok.name(u'Unternehmen verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "unternehmencontrol"
    viewURL = "unternehmencontrol"

    @property
    def url(self):
        return "%s/%s" % (url(self.request, self.context), self.viewURL)


class AddUnternehmen(PageAddForm, grok.View):
    grok.context(IFernlehrgangApp)
    title = u'Unternehmen'
    label = u'Unternehmen anlegen'

    fields = Fields(IUnternehmen)

    def create(self, data):
        return Unternehmen(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        return self.url(self.context, 'unternehmencontrol')




class UnternehmenControl(DeleteFormTablePage, grok.View):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmencontrol')
    extends(DeleteFormTablePage)
    title = u"Unternehmen"
    description = u"Hier können Sie die Unternehmen der BG-Verwalten"

    cssClasses = {'table': 'tablesorter myTable'}
    status = None

    @property
    def values(self):
        root = getSite()
        session = Session()
        for unternehmen in session.query(Unternehmen).all():
            locate(root, unternehmen, DefaultModel)
            yield unternehmen 


    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'unternehmencontrol')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Unternehmen anlegen')
    def handleAddUnternehmen(self, action):
         self.redirect(self.url(self.context, 'addunternehmen')) 


class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgangApp)
    weight = 0

class Mitgliedsnummer(GetAttrColumn):
    grok.name('Mitgliedsnummer')
    grok.context(IFernlehrgangApp)
    weight = 10
    header = u"Mitgliedsnummer"
    attrName = u"mnr"

class Name(GetAttrColumn):
    grok.name('Name')
    grok.context(IFernlehrgangApp)
    weight = 20
    header = u"Name"
    attrName = u"name"

class Aktion(LinkColumn):
    grok.name('aktion')
    grok.context(IFernlehrgangApp)
    weight = 99
    linkContent = "edit"


class Index(PageDisplayForm, grok.View):
    grok.context(IUnternehmen)
    fields = Fields(IUnternehmen)
