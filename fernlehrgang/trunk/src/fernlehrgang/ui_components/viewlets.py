# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from uvc.layout.layout import IUVCLayer
from fernlehrgang.models import Fernlehrgang
from dolmen.app.layout import master, viewlets, IDisplayView, MenuViewlet
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



class ObjectActionMenu(viewlets.ContextualActions):
    grok.name('contextualactions')
    grok.layer(IUVCLayer)
    grok.title('Actions')

    menu_class = u"foldable menu"
    title = "Actions"

    def get_actions(self, context):
        return MenuViewlet.get_actions(self, context)



class AddMenu(menu.Menu):
    grok.name('uvcsite-addmenu')
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.title('Add')
    
    menu_class = u"foldable menu"


class AddMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.viewletmanager(master.Top)
    grok.order(70)

    def render(self):
        menu = AddMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


class NavigationMenu(menu.Menu):
    grok.name('navigation')
    grok.title('Navigation')
    grok.context(Interface)
    menu_class = u'menu'


class NavigationMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.viewletmanager(master.AboveBody)
    
    def render(self):
        menu = NavigationMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


class MenuTemplate(pagetemplate.PageTemplate):
    pagetemplate.view(IAboveContent)
    template = grok.PageTemplateFile("templates/menu.pt")
