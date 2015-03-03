# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from time import time
from plone.memoize import ram
from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from fernlehrgang.interfaces import IListing
from fernlehrgang.models import Fernlehrgang
from dolmen.app.layout import master, viewlets, IDisplayView, MenuViewlet
from uvc.layout.interfaces import IAboveContent, IFooter, IPageTop
from uvc.layout import IPersonalPreferences, MenuItem 
from grokcore.chameleon.components import ChameleonPageTemplateFile
from uvc.layout.slots import managers


grok.templatedir('templates')

class UserName(MenuItem):
    """ User Viewlet"""
    grok.name('myname')
    grok.context(Interface)
    grok.viewletmanager(IPersonalPreferences)
    grok.order(300)
    action =""

    @property
    def title(self):
        return self.request.principal.description or self.request.principal.id


#
## Global Menu
#


class GlobalMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.viewletmanager(IPageTop)
    template = ChameleonPageTemplateFile('templates/globalmenu.cpt')
    grok.order(11)
    flgs = []

    @ram.cache(lambda *args: time() // (60 * 60))
    def getContent(self):
        session = Session()
        d = {}
        for fernlehrgang in session.query(Fernlehrgang).all():
            url = "%s/fernlehrgang/%s" % (
                self.view.layout.application_url(), fernlehrgang.id)
            titel = fernlehrgang.titel
            if not fernlehrgang.jahr in d.keys():
                d[fernlehrgang.jahr] = []
            d[fernlehrgang.jahr].append(dict(url=url, title=titel))
        return d

    def update(self):
        self.flgs = self.getContent()


#
## Object Menu
#


class ObjectActionMenu(viewlets.ContextualActions):
    grok.name('contextualactions')
    grok.title('Actions')
    grok.viewletmanager(IAboveContent)
    grok.order(119)

    menu_template = ChameleonPageTemplateFile('templates/objectmenu.cpt')

    id = "uvcobjectmenu"
    menu_class = u"foldable menu"
    title = "Menu"

    def available(self):
        if IListing.providedBy(self.view):
            return False 
        return True

#
## Add Menu
#

class AddMenu(menu.Menu):
    grok.name('uvcsite-addmenu')
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.title(u'Hinzufügen')
    menu_class = u'nav nav-pills'


class AddMenuTemplate(pagetemplate.PageTemplate):
    grok.view(AddMenu)


class AddMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.viewletmanager(IAboveContent)
    grok.order(120)

    def render(self):
        menu = AddMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()

#
## Navigation
#

class NavigationMenu(menu.Menu):
    grok.name('navigation')
    grok.title('Navigation')
    grok.context(Interface)
    menu_class = u'nav nav-tabs'


class NavigationMenuTemplate(pagetemplate.PageTemplate):
    grok.view(NavigationMenu)


class NavigationMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.viewletmanager(IAboveContent)
    grok.order(100)
    
    def render(self):
        menu = NavigationMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


#
## FavIcon
#

class FavIcon(grok.Viewlet):
    grok.viewletmanager(managers.Headers)
    grok.context(Interface)
