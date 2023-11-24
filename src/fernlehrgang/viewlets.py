# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


import grok
import collections

import uvc.menus.components
import uvc.menus.directives

from zope.interface import Interface
from fernlehrgang.slots.managers import AboveContent
from grokcore.message import receive


grok.templatedir('templates')


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
    grok.require('uvc.managefernlehrgang')


class AddEntry(uvc.menus.components.MenuItem):
    grok.context(Interface)
    uvc.menus.directives.menu(AddMenu)
    grok.baseclass()


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
    grok.order(10)

    bound_menus = ('navigation',)

    def update(self):
        self.menus = collections.OrderedDict(
            uvc.menus.components.menus_iterator(
                self.context, self.request, self.view, *self.bound_menus))


class FlashMessages(grok.Viewlet):
    grok.order(00)
    grok.context(Interface)
    grok.name('uvcsite.messages')
    grok.viewletmanager(AboveContent)

    def update(self):
        received = receive()
        if received is not None:
            self.messages = list(received)
        else:
            self.messages = []
#
## FavIcon
#

#class FavIcon(grok.Viewlet):
#    grok.viewletmanager(managers.Headers)
#    grok.context(Interface)
