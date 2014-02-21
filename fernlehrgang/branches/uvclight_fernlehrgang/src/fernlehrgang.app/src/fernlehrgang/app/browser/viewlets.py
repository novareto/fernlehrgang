# -*- coding: utf-8 -*-

import uvclight

from dolmen import menu
from fernlehrgang.models import Fernlehrgang
from plone.memoize import ram
from time import time
from uvclight import MenuItem
from uvc.tb_layout.menuviewlets import ContextualActionsMenuViewlet
from uvclight.interfaces import IPersonalPreferences
from uvclight.interfaces import IAboveContent, IPageTop, IHeaders
from zope.interface import Interface
from cromlech.sqlalchemy import get_session

from . import pagetemplate
from ..wsgi import IFernlehrgangSkin
from ..interfaces import IListing


class UserName(MenuItem):
    """ User Viewlet
    """
    uvclight.name('myname')
    uvclight.context(Interface)
    uvclight.menu(IPersonalPreferences)
    uvclight.order(300)
    uvclight.layer(IFernlehrgangSkin)

    action = ""

    @property
    def title(self):
        principal = uvclight.current_principal()
        return principal.description or principal.id


#
## Global Menu
#

class GlobalMenuViewlet(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IPageTop)
    uvclight.layer(IFernlehrgangSkin)

    template = pagetemplate('globalmenu.cpt')
    uvclight.order(11)
    flgs = []

    @ram.cache(lambda *args: time() // (60 * 60))
    def getContent(self):
        session = get_session('fernlehrgang')
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


class ObjectActionMenu(ContextualActionsMenuViewlet):
    uvclight.name('contextualactions')
    uvclight.title('Actions')
    uvclight.viewletmanager(IAboveContent)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(119)

    menu_template = pagetemplate('objectmenu.cpt')

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
    uvclight.name('uvcsite-addmenu')
    uvclight.context(Interface)
    uvclight.title(u'Hinzufügen')
    uvclight.layer(IFernlehrgangSkin)

    menu_class = u'nav nav-pills'


class AddMenuViewlet(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(120)
    uvclight.layer(IFernlehrgangSkin)

    template = ''
    
    def render(self):
        menu = AddMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()

#
## Navigation
#

class NavigationMenu(menu.Menu):
    uvclight.name('navigation')
    uvclight.title('Navigation')
    uvclight.context(Interface)
    uvclight.layer(IFernlehrgangSkin)

    menu_class = u'nav nav-tabs'


class NavigationMenuViewlet(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IAboveContent)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(100)

    template = ''
    
    def render(self):
        menu = NavigationMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()
