# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft 
from uvc.layout.interfaces import ISidebar
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.flg import IFernlehrgang
from megrok.z3ctable.ftests import Container, Content
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable import CheckBoxColumn, LinkColumn, GetAttrColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from dolmen.menu import menuentry
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from dolmen.app.layout import models, ContextualMenuEntry


grok.templatedir('templates')


@menuentry(NavigationMenu)
class LehrhefteListing(DeleteFormTablePage):
    grok.context(IFernlehrgang)
    grok.name('lehrhefte_listing')
    grok.title(u'Lehrhefte verwalten')
    title = u"Lehrhefte"
    description = u"Hier können Sie die Lehrhefte zu Ihrem Fernlehrgang bearbeiten."
    extends(DeleteFormTablePage)
    cssClasses = {'table': 'tablesorter myTable'}

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
        self.nextURL = self.url(self.context, 'lehrhefte_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

    @button.buttonAndHandler(u'Lehrheft anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addlehrheft')) 


@menuentry(AddMenu)
class AddLehrheft(PageAddForm):
    grok.context(IFernlehrgang)
    grok.title(u'Lehrheft')
    title = u'Lehrheft'
    label = u'Lehrheft anlegen'
    description = u'Lehrheft anlegen'

    fields = Fields(ILehrheft).omit('id')

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.object = object
        self.context.lehrhefte.append(object)

    def nextURL(self):
        return self.url(self.context, 'lehrhefte_listing')


class Index(models.DefaultView):
    grok.context(ILehrheft)
    grok.name('index')
    title = label = u"Lehrheft"
    description = u"Details zu Ihrem Lehrheft"
    fields = Fields(ILehrheft).omit(id)


class Edit(models.Edit):
    grok.context(ILehrheft)
    grok.title(u'Edit')
    grok.name('edit')

    fields = Fields(ILehrheft).omit('id')

    @button.buttonAndHandler(u'Lehrhefte entfernen')
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
    

class Nummer(GetAttrColumn):
    grok.name('nummer')
    grok.context(IFernlehrgang)
    weight = 10 
    attrName = "nummer"
    header = "Nummer"


class Name(LinkColumn):
    grok.name('Nummer')
    grok.context(IFernlehrgang)
    weight = 99
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.titel
