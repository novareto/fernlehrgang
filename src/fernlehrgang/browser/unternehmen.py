# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from dolmen.menu import menuentry
from megrok.traject import locate
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Unternehmen 
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.app import IFernlehrgangApp 
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from megrok.z3ctable import CheckBoxColumn, LinkColumn, GetAttrColumn 
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends

from dolmen.app.layout import IDisplayView, ContextualMenuEntry
from dolmen.app.layout import models
from dolmen.menu import menuentry
from fernlehrgang.ui_components import AddMenu, NavigationMenu



grok.templatedir('templates')

@menuentry(NavigationMenu)
class UnternehmenListing(DeleteFormTablePage):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmen_listing')
    grok.title(u"Unternehmen verwalten")
    title = "Unternehmen verwalten"
    description = u"Hier können Sie die Unternehmen der BG-Verwalten"
    extends(DeleteFormTablePage)

    cssClasses = {'table': 'tablesorter myTable'}
    status = None

    @property
    def values(self):
        root = getSite()
        session = Session()
        for unternehmen in session.query(Unternehmen).filter(Unternehmen.plz == "91438").all():
            locate(root, unternehmen, DefaultModel)
            yield unternehmen 


    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'unternehmen_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True

    @button.buttonAndHandler(u'Unternehmen anlegen')
    def handleAddUnternehmen(self, action):
         self.redirect(self.url(self.context, 'addunternehmen')) 


class Index(models.DefaultView):
    grok.context(IUnternehmen)
    grok.name('index')
    title = u"Unternehmen"
    label = u"Unternehmen"
    description = u"Details zu Ihrem Unternehmen"

    fields = Fields(IUnternehmen)


@menuentry(AddMenu)
class AddUnternehmen(PageAddForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Unternehmen')
    title = u'Unternehmen'
    label = u'Unternehmen anlegen'
    description = u"Unternehmen anlegen"

    fields = Fields(IUnternehmen)

    def create(self, data):
        return Unternehmen(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        return self.url(self.context, 'unternehmen_listing')


class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgangApp)
    weight = 0
    cssClasses = {'th': 'checkBox'}


class Mitgliedsnummer(LinkColumn):
    grok.name('Mitgliedsnummer')
    grok.context(IFernlehrgangApp)
    weight = 10
    header = u"Mitgliedsnummer"

    def getLinkContent(self, item):
        return item.mnr


class Name(GetAttrColumn):
    grok.name('Name')
    grok.context(IFernlehrgangApp)
    weight = 20
    header = u"Name"
    attrName = u"name"
