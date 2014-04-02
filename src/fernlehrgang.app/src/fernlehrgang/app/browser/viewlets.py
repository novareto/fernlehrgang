# -*- coding: utf-8 -*-

import uvclight

from cromlech.sqlalchemy import get_session
from dolmen import menu
from dolmen.message.utils import receive as receive_messages
from fernlehrgang.models import Fernlehrgang
from plone.memoize import ram
from time import time
from uvc.design.canvas.menus import *
from uvclight import MenuItem
from uvclight.interfaces import IAboveContent, IPageTop, IHeaders
from uvclight.interfaces import IPersonalMenu, IContextualActionsMenu
from zope.i18n import translate
from zope.interface import Interface, implementer

from . import pagetemplate
from ..wsgi import IFernlehrgangSkin
from ..interfaces import IListing


#
## Global Menu
#

class GlobalMenuViewlet(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IPageTop)
    uvclight.layer(IFernlehrgangSkin)

    template = uvclight.get_template('globalmenu.cpt', __file__)
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

class ObjectActionMenuViewlet(uvclight.Viewlet):
    uvclight.name('contextualactions')
    uvclight.title('Actions')
    uvclight.viewletmanager(IAboveContent)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(119)

    def available(self):
        if IListing.providedBy(self.view):
            return False 
        return True

    def render(self):
        menu = ContextualActionsMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()
    
#
## Add Menu
#


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
## Personal menu
#

class PersonalMenuViewlet(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IPageTop)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(100)
    
    def render(self):
        menu = PersonalMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


class UserName(MenuItem):
    """ User Viewlet
    """
    uvclight.name('myname')
    uvclight.context(Interface)
    uvclight.menu(IPersonalMenu)
    uvclight.order(300)
    uvclight.layer(IFernlehrgangSkin)

    action = ""
    icon = "glyphicon glyphicon-user"

    def __init__(self, *args, **kwargs):
        MenuItem.__init__(self, *args, **kwargs)
        menu = UserMenu(self.context, self.request, self.view)
        menu.update()
        self.menu = menu
        
    @property
    def css(self):
        return self.menu.viewlets and "dropdown" or ""

    def render(self):
        return self.menu.render()


class ClickMe(MenuItem):
    """ User Viewlet
    """
    uvclight.name('clickme')
    uvclight.context(Interface)
    uvclight.menu(UserMenu)
    uvclight.order(300)
    uvclight.layer(IFernlehrgangSkin)

    action = "test"
    
    
#
## Navigation
#


class NavigationMenuViewlet(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IAboveContent)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(100)

    def render(self):
        menu = NavigationMenu(self.context, self.request, self.view)
        menu.update()
        return menu.render()


class FlashMessages(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IPageTop)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(200)

    def render(self):
        messages = receive_messages(type=None)
        dd = [x for x in messages]
        return ""
        if messages:
            print "MESSAGE SHOULD COME"
            return ('<div class="messages">' +
                    "\n".join('<div class="%s">%s</div>' %
                              (m.type, translate(
                                  m.message, context=self.request))
                              for m in messages) +
                    '</div>')
        return ''
