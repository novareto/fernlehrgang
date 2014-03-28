# -*- coding: utf-8 -*-

import uvclight

from cromlech.sqlalchemy import get_session
from dolmen import menu
from dolmen.message.utils import receive as receive_messages
from fernlehrgang.models import Fernlehrgang
from plone.memoize import ram
from time import time
from uvclight import MenuItem
from uvclight.interfaces import IAboveContent, IPageTop, IHeaders
from uvclight.interfaces import IPersonalPreferences, IContextualActionsMenu
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

@implementer(IContextualActionsMenu)
class ContextualActionsMenu(menu.Menu):
    uvclight.name('contextualactionsmenu')
    uvclight.title(u"Actions")
    
    template = uvclight.get_template('objectmenu.cpt', __file__)
    menu_class = u'nav nav-pills pull-right'
    css = "actions_menu"


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

class AddMenu(menu.Menu):
    uvclight.name('uvcsite-addmenu')
    uvclight.context(Interface)
    uvclight.title(u'Hinzufügen')
    uvclight.layer(IFernlehrgangSkin)

    template = uvclight.get_template('addmenutemplate.cpt', __file__)

    menu_class = u'nav nav-pills pull-right'
    css = "addmenu"


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

@implementer(IPersonalPreferences)
class PersonalMenu(menu.Menu):
    uvclight.name('personal')
    uvclight.title('Personal menu')
    uvclight.context(Interface)
    uvclight.layer(IFernlehrgangSkin)
    template = uvclight.get_template('personal.cpt', __file__) 

    menu_class = u'nav nav-tabs'
    css = "navigation"


class UserMenu(menu.Menu):
    uvclight.name('useractions')
    uvclight.title('User actions')
    uvclight.context(Interface)
    uvclight.layer(IFernlehrgangSkin)
    template = uvclight.get_template('useractions.cpt', __file__) 

    menu_class = u'nav nav-tabs'
    css = "navigation"
    
    def standalone(self):
        return self.request.application_url + "/meine_daten"
    
    @property
    def username(self):
        principal = uvclight.current_principal()
        return principal.description or principal.id

    
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
    uvclight.menu(IPersonalPreferences)
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

class NavigationMenu(menu.Menu):
    uvclight.name('navigation')
    uvclight.title('Navigation')
    uvclight.context(Interface)
    uvclight.layer(IFernlehrgangSkin)
    template = uvclight.get_template('navigationmenutemplate.cpt', __file__) 

    menu_class = u'nav nav-tabs'
    css = "navigation"


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
