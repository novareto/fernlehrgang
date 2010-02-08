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
from fernlehrgang.models import Fernlehrgang
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.ui_components.viewlets import AboveContent
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang
from megrok.z3ctable import CheckBoxColumn, LinkColumn, GetAttrColumn 
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends


grok.templatedir('templates')


class AddFLGMenu(MenuItem):
    grok.context(IFernlehrgangApp)
    grok.name(u'Fernlehrgänge verwalten')
    grok.viewletmanager(ISidebar)

    urlEndings = "fernlehrgang_listing"
    viewURL = "fernlehrgang_listing"


@menuentry(AboveContent, title=u"Fernlehrgänge verwalten", order=20)
class FernlehrgangListing(DeleteFormTablePage, grok.View):
    grok.context(IFernlehrgangApp)
    grok.name('fernlehrgang_listing')
    extends(DeleteFormTablePage)
    title = u"Fernlehrgänge"
    description = u"Hier können Sie die Fernlehrgaenge der BG-Verwalten"

    cssClasses = {'table': 'tablesorter myTable'}
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
        self.nextURL = self.url(self.context, 'fernlehrgang_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

    @button.buttonAndHandler(u'Fernlehrgang anlegen')
    def handleAddUnternehmen(self, action):
         self.redirect(self.url(self.context, 'addfernlehrgang')) 



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
    title = u"Fernlehrgang"
    description = u"Details zu Ihrem Fernlehrgang"

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

### Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgangApp)
    weight = 0
    cssClasses = {'th': 'checkBox'}


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


