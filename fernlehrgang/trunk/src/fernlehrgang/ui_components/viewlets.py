# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from fernlehrgang.models import Fernlehrgang
from uvc.layout.interfaces import IGlobalMenu, IAboveContent


class GlobalMenu(grok.ViewletManager):
    grok.name('uvcsite.globalmenu')
    grok.context(Interface)
    grok.implements(IGlobalMenu)
    template = grok.PageTemplateFile('globalmenu.pt')

    css = ['blue', 'orange', 'violet', 'green', 'brown', 'purple']

    def getClass(self, index):
        return self.css[index]

    @property
    def flgs(self):
        session = Session()
        rc = []
        for i, fernlehrgang in enumerate(session.query(Fernlehrgang).all()):
            url = "%s/fernlehrgang/%s" %(self.view.application_url(), fernlehrgang.id)
            rc.append(dict(title=fernlehrgang.jahr, css=self.css[i], url=url))
        return rc    


class AboveContent(menu.Menu):
    grok.name('uvcsite.abovecontent')
    grok.context(Interface)
    grok.implements(IAboveContent)


class MenuTemplate(pagetemplate.PageTemplate):
    pagetemplate.view(IAboveContent)
    template = grok.PageTemplateFile("templates/menu.pt")
