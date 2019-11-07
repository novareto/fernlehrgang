# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


import grok
import collections

from time import time
from plone.memoize import ram

import uvc.menus.components
import uvc.menus.directives

#from dolmen import menu
from megrok import pagetemplate
from z3c.saconfig import Session
from zope.interface import Interface
from fernlehrgang.interfaces import IListing
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.slots.managers import AboveContent
#from dolmen.app.layout import master, viewlets, IDisplayView, MenuViewlet
#from uvc.layout.interfaces import IAboveContent, IFooter, IPageTop
#from uvc.layout import IPersonalPreferences, MenuItem
from grokcore.chameleon.components import ChameleonPageTemplateFile
#from uvc.layout.slots import managers
#from uvc.layout.slots.menuviewlets import PersonalPreferencesViewlet, PersonalPreferencesTemplate
#from uvc.tbskin.skin import ITBSkinLayer

grok.templatedir('templates')


#class PersonalPreferencesTemplate(PersonalPreferencesTemplate):
#    grok.view(PersonalPreferencesViewlet)
#    grok.layer(ITBSkinLayer)
##    template = None
#
#    def render(self):
#        return u"HALLLO"


#class UserName(MenuItem):
#    """ User Viewlet"""
#    grok.name('myname')
#    grok.context(Interface)
#    grok.viewletmanager(IPersonalPreferences)
#    grok.order(300)
#    action =""

#    @property
#    def title(self):
#        return self.request.principal.description or self.request.principal.id


#
## Global Menu
#


#class GlobalMenuViewlet(grok.Viewlet):
#    grok.context(Interface)
#    grok.viewletmanager(IPageTop)
#    template = ChameleonPageTemplateFile('templates/globalmenu.cpt')
#    grok.order(11)
#    flgs = []

#    @ram.cache(lambda *args: time() // (60 * 60))
#    def getContent(self):
#        session = Session()
#        d = {}
#        for fernlehrgang in session.query(Fernlehrgang).all():
#            url = "%s/fernlehrgang/%s" % (
 #               self.view.application_url(), fernlehrgang.id)
 #           titel = fernlehrgang.titel
 #           if not fernlehrgang.jahr in d.keys():
 #               d[fernlehrgang.jahr] = []
 #           d[fernlehrgang.jahr].append(dict(url=url, title=titel))
 #       return d

 #   def update(self):
 #       self.flgs = self.getContent()


#
## Object Menu
#


#class ObjectActionMenu(viewlets.ContextualActions):
#    grok.name('contextualactions')
#    grok.title('Actions')
#    grok.viewletmanager(IAboveContent)
#    grok.order(119)
#
#    menu_template = ChameleonPageTemplateFile('templates/objectmenu.cpt')
#
#    id = "uvcobjectmenu"
#    menu_class = u"foldable menu"
#    title = "Menu"
#
#    def available(self):
#        if IListing.providedBy(self.view):
#            return False
#        return True

#
## Add Menu
#

class ObjectMenu(uvc.menus.components.Menu):
    grok.name('objectmenu')
    grok.context(Interface)
    grok.title('Object')


class ObjectEntry(uvc.menus.components.MenuItem):
    grok.context(Interface)
    uvc.menus.directives.menu(ObjectMenu)
    grok.baseclass()

    title = "Dummy"


class AddMenu(uvc.menus.components.Menu):
    grok.name('addmenu')
    grok.context(Interface)
    grok.title('Hinzufgen')


class AddEntry(uvc.menus.components.MenuItem):
    grok.name('dummy')
    grok.context(Interface)
    uvc.menus.directives.menu(AddMenu)
    grok.baseclass()

    title = "Fernlehrgang"
    

class AddMenuRenderer(grok.Viewlet):
    grok.context(Interface)
    grok.template('addmenu')
    grok.viewletmanager(AboveContent)
    grok.order(10)

    bound_menus = ('addmenu', 'objectmenu')

    def update(self):
        self.menus = collections.OrderedDict(
            uvc.menus.components.menus_iterator(
                self.context, self.request, self.view, *self.bound_menus))


class NavigationMenu(uvc.menus.components.Menu):
    grok.name('navigation')
    grok.title('Navigation')
    grok.context(Interface)


class NavEntry(uvc.menus.components.MenuItem):
    grok.name('dummy')
    grok.context(Interface)
    uvc.menus.directives.menu(NavigationMenu)
    grok.baseclass()

    title = "Dummy"
    

class NavigationMenuRenderer(grok.Viewlet):
    grok.context(Interface)
    grok.template('navigation')
    grok.viewletmanager(AboveContent)
    grok.order(00)

    bound_menus = ('navigation',)

    def update(self):
        self.menus = collections.OrderedDict(
            uvc.menus.components.menus_iterator(
                self.context, self.request, self.view, *self.bound_menus))

#
## FavIcon
#

#class FavIcon(grok.Viewlet):
#    grok.viewletmanager(managers.Headers)
#    grok.context(Interface)
