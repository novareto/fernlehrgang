# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from fernlehrgang import Page
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang

from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields
from z3c.saconfig import Session

grok.templatedir('templates')

class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp) 


class Index(Page):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Fernlehrgang"

    def getFernlehrgaenge(self):
        session = Session()
        return session.query(Fernlehrgang).all() 


class AddMenu(MenuItem):
    grok.context(IFernlehrgangApp)
    grok.name(u'Fernlehrgang anlegen')
    grok.viewletmanager(ISidebar)

    urlEndings = "add"
    viewURL = "add"


class Add(PageAddForm, grok.View):
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

class FIndex(PageDisplayForm, grok.View):
    grok.context(IFernlehrgang)
    grok.name('index')

    fields = Fields(IFernlehrgang).omit('id')
