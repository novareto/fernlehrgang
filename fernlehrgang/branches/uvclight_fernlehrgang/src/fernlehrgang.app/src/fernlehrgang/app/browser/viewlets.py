# -*- coding: utf-8 -*-

import grok

from dolmen import menu
from dolmen.app.layout import viewlets, IDisplayView
from fernlehrgang.models import Fernlehrgang
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok import pagetemplate
from plone.memoize import ram
from time import time
from uvc.layout import IPersonalPreferences, MenuItem 
from uvc.layout.interfaces import IAboveContent, IPageTop
from uvc.layout.interfaces import IHeaders
from uvc.layout.slots import managers
from z3c.saconfig import Session
from zope.app.appsetup.product import getProductConfiguration
from zope.interface import Interface
from zope.interface import Interface

from .skin import IFernlehrgangSkin
from ..interfaces import IListing


grok.templatedir('templates')


class TestSystem(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def update(self):
        config = getProductConfiguration('database')
        DSN = config['dsn']
        if DSN.startswith('oracle://novareto:retonova@10.30.4.95/BGETest'):
            self.view.flash(u"Test - System", type="info")
        self.view.flash(u"Test - System", type="info")

    def render(self):
        return ""


class UserName(MenuItem):
    """ User Viewlet
    """
    grok.name('myname')
    grok.context(Interface)
    grok.viewletmanager(IPersonalPreferences)
    grok.order(300)
    grok.layer(IFernlehrgangSkin)

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
    grok.layer(IFernlehrgangSkin)

    template = ChameleonPageTemplateFile('templates/globalmenu.cpt')
    grok.order(11)
    flgs = []

    @ram.cache(lambda *args: time() // (60 * 60))
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


#
## Object Menu
#


class ObjectActionMenu(viewlets.ContextualActions):
    grok.name('contextualactions')
    grok.title('Actions')
    grok.viewletmanager(IAboveContent)
    grok.layer(IFernlehrgangSkin)
    grok.order(119)

    menu_template = ChameleonPageTemplateFile('templates/objectmenu.cpt')

    id = "uvcobjectmenu"
    menu_class = u"foldable menu"
    title = "Menu"

    def available(self):
        if IListing.providedBy(self.view):
            return True
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
    grok.layer(IFernlehrgangSkin)

    menu_class = u'nav nav-pills'


class AddMenuTemplate(pagetemplate.PageTemplate):
    grok.view(AddMenu)
    grok.layer(IFernlehrgangSkin)


class AddMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.view(IDisplayView)
    grok.viewletmanager(IAboveContent)
    grok.order(120)
    grok.layer(IFernlehrgangSkin)

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
    grok.layer(IFernlehrgangSkin)

    menu_class = u'nav nav-tabs'


class NavigationMenuTemplate(pagetemplate.PageTemplate):
    grok.view(NavigationMenu)
    grok.layer(IFernlehrgangSkin)


class NavigationMenuViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.viewletmanager(IAboveContent)
    grok.layer(IFernlehrgangSkin)
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
    grok.layer(IFernlehrgangSkin)
