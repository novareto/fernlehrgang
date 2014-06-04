# -*- coding: utf-8 -*-

import uvclight
from uvclight.interfaces import IFooterMenu, IPersonalMenu
from uvclight.security import unauthenticated_principal
from uvclight.utils import current_principal
from zope.interface import Interface


class KontaktMI(uvclight.MenuItem):
    uvclight.context(Interface)
    uvclight.title(u"Kontakt")
    uvclight.menu(IFooterMenu)

    @property
    def action(self):
        return self.view.application_url() + '/kontakt'


class Logout(uvclight.MenuItem):
    uvclight.context(Interface)
    uvclight.title(u"Abmelden")
    uvclight.menu(IPersonalMenu)

    icon = "glyphicons unlock"

    @property
    def available(self):
        principal = current_principal()
        return principal is not unauthenticated_principal

    @property
    def action(self):
        return self.view.application_url() + '/logout'
