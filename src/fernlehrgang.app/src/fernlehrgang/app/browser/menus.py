# -*- coding: utf-8 -*-

import uvclight
from uvclight.interfaces import IFooterMenu, IPersonalMenu
from zope.interface import Interface


class KontaktMI(uvclight.MenuItem):
    uvclight.context(Interface)
    uvclight.title(u"Kontakt")
    uvclight.menu(IFooterMenu)

    @property
    def action(self):
        return self.view.application_url() + '/kontakt'


class LogoutMI(uvclight.MenuItem):
    uvclight.context(Interface)
    uvclight.title(u"Abmelden")
    uvclight.menu(IPersonalMenu)

    icon = "glyphicons unlock"
    
    @property
    def action(self):
        return self.view.application_url() + '/logout'
