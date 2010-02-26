# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from fernlehrgang.models import Fernlehrgang
from dolmen.app.layout import master
from uvc.layout.interfaces import IAboveContent


class GlobalMenu(grok.Viewlet):
    grok.name('uvcsite.globalmenu')
    grok.context(Interface)
    grok.viewletmanager(master.Top)
    template = grok.PageTemplateFile('templates/globalmenu.pt')
    grok.order(1)

    css = ['blue', 'orange', 'violet', 'green', 'brown', 'purple']

    def getClass(self, index):
        return self.css[index]

    def getContent(self):
        session = Session()
        rc = []
        for i, fernlehrgang in enumerate(session.query(Fernlehrgang).all()):
            url = "%s/fernlehrgang/%s" % (
                self.view.application_url(), fernlehrgang.id)
            rc.append(dict(title=fernlehrgang.jahr, css=self.css[i], url=url))
        return rc    

    def update(self):
        self.flgs = self.getContent()


class AboveContent(menu.Menu):
    grok.name('uvcsite.abovecontent')
    grok.context(Interface)
    grok.implements(IAboveContent)


class PersonalPreferences(menu.Menu):
    grok.name('uvcsite.personalpreferences')
    grok.context(Interface)
    grok.implements(IAboveContent)
    grok.title('')


class MenuTemplate(pagetemplate.PageTemplate):
    pagetemplate.view(IAboveContent)
    template = grok.PageTemplateFile("templates/menu.pt")
