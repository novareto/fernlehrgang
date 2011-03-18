# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from uvc.layout.layout import IUVCLayer
from fernlehrgang.interfaces import IListing
from fernlehrgang.models import Fernlehrgang
from dolmen.app.layout import master, viewlets, IDisplayView, MenuViewlet
from uvc.layout.interfaces import IAboveContent, IFooter, IPageTop
from uvc.layout.menus import PersonalPreferences 


class UserName(grok.Viewlet):
    """ User Viewlet"""
    grok.name('myname')
    grok.context(Interface)
    grok.viewletmanager(PersonalPreferences)
    grok.order(14)
    group = ""

    def render(self):
        return '<a href="#"> %s </a>' % self.request.principal.description or self.request.principal.id


class GlobalMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.viewletmanager(IPageTop)
    template = grok.PageTemplateFile('templates/globalmenu.pt')
    grok.order(11)
    flgs = []


    def getCss(self, flg):
        css = {'2011': 'blue',
               '2012': 'orange',
               '2013': 'violet', 
               '2014': 'green',
               '2015': 'brown', 
               '2016': 'purple'}
        return "dropdown %s" % css[flg]

    def getContent(self):
        session = Session()
        d = {}
        for fernlehrgang in session.query(Fernlehrgang).all():
            url = "%s/fernlehrgang/%s" % (
                self.view.application_url(), fernlehrgang.id)
            titel = fernlehrgang.titel
            if not fernlehrgang.jahr in d.keys():
                d[fernlehrgang.jahr] = []
            d[fernlehrgang.jahr].append(dict(url=url, title=titel))
        return d 

    def update(self):
        self.flgs = self.getContent()


class ObjectActionMenu(viewlets.ContextualActions):
    grok.name('contextualactions')
    grok.layer(IUVCLayer)
    grok.title('Actions')
    grok.viewletmanager(master.AboveBody)
    grok.order(50)

    menu_template = grok.PageTemplateFile('templates/objectmenu.pt')

    id = "uvcobjectmenu"
    menu_class = u"foldable menu"
    title = "Menu"

    def available(self):
        if IListing.providedBy(self.view):
            return False 
        return True


class AddMenu(menu.Menu):
    grok.name('uvcsite-addmenu')
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.title(u'Hinzufügen')
    
    menu_class = u"foldable menu"


class AddMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.viewletmanager(master.AboveBody)
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
    grok.order(15)
    
    def render(self):
        menu = NavigationMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


class MenuTemplate(pagetemplate.PageTemplate):
    pagetemplate.view(IAboveContent)
    template = grok.PageTemplateFile("templates/menu.pt")
