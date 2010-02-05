# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from megrok.traject import locate
from fernlehrgang.utils import Page
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang

from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from z3c.saconfig import Session


from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable import CheckBoxColumn, LinkColumn, GetAttrColumn 
from megrok.z3ctable.ftests import Container, Content

from grok import url, getSite

from megrok.traject.components import DefaultModel

grok.templatedir('templates')


class AddFLGMenu(MenuItem):
    grok.context(IFernlehrgangApp)
    grok.name(u'Fernlehrgaengeverwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "flgcontrol"
    viewURL = "flgcontrol"



class FlgControl(DeleteFormTablePage, grok.View):
    grok.context(IFernlehrgangApp)
    grok.name('flgcontrol')
    extends(DeleteFormTablePage)
    title = u"Fernlehrgaenge"
    description = u"Hier können Sie die Fernlehrgaenge der BG-Verwalten"

    status = None

    @property
    def values(self):
        root = getSite()
        session = Session()
        for fernlehrgang in session.query(Fernlehrgang).all():
            locate(root, fernlehrgang, DefaultModel)
            yield fernlehrgang 


    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'flgcontrol')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()

    @button.buttonAndHandler(u'Fernlehrgang anlegen')
    def handleAddUnternehmen(self, action):
         self.redirect(self.url(self.context, 'addfernlehrgang')) 


class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgangApp)
    weight = 0

class Title(LinkColumn):
    grok.name('titel')
    grok.context(IFernlehrgangApp)
    weight = 10
    header = u"Titel"
    attrName = u"titel"

    def getLinkContent(self, item):
        return item.titel


class Jahr(GetAttrColumn):
    grok.name('Jahr')
    grok.context(IFernlehrgangApp)
    weight = 20
    header = u"Jahr"
    attrName = u"jahr"



class AddFernlehrgang(PageAddForm, grok.View):
    grok.context(IFernlehrgangApp)
    title = u'Fernlehrgang'
    label = u'Fernlehrgang anlegen'

    fields = Fields(IFernlehrgang).omit('id')

    def create(self, data):
        return Fernlehrgang(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        url = self.url(self.context)
        return url


class Index(PageDisplayForm, grok.View):
    grok.context(IFernlehrgang)
    grok.name('index')

    fields = Fields(IFernlehrgang).omit('id')


class Edit(PageEditForm, grok.View):
    grok.context(IFernlehrgang)
    grok.name('edit')

    fields = Fields(IFernlehrgang).omit('id')

    @button.buttonAndHandler(u'Fernlehrgang entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 
