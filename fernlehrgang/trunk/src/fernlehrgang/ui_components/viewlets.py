# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from fernlehrgang.models import Fernlehrgang
from dolmen.app.layout import master, IDisplayView
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


class AddMenu(menu.Menu):
    grok.name('uvcsite-addmenu')
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.title('Add')

    menu_class = u"foldable menu"


class AddMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.viewletmanager(master.AboveBody)

    def render(self):
        menu = AddMenu(self.context, self.request, self.view)
        menu.update()
        js = """<script src="%s"></script>""" % self.static['dropdown.js']()
        return js + menu.render()


class ObjectMenu(menu.Menu):
    grok.name('object-menu')
    grok.title('Object actions')
    grok.context(Interface)
    grok.view(IDisplayView)

    menu_class = u'object menu'


class ObjectMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.viewletmanager(master.AboveBody)
    
    def render(self):
        menu = ObjectMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


class MenuTemplate(pagetemplate.PageTemplate):
    pagetemplate.view(IAboveContent)
    template = grok.PageTemplateFile("templates/menu.pt")
