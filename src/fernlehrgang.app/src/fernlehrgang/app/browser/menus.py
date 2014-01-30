# -*- coding: utf-8 -*-

import grok

from uvc.layout import MenuItem
from uvc.layout.interfaces import IFooter, IPersonalPreferences
from zope.interface import Interface


class KontaktMI(MenuItem):
    grok.context(Interface)
    grok.title(u"Kontakt")
    grok.viewletmanager(IFooter)

    @property
    def action(self):
        return self.view.application_url() + '/kontakt'


class LogoutMI(MenuItem):
    grok.context(Interface)
    grok.title(u"Abmelden")
    grok.viewletmanager(IPersonalPreferences)

    @property
    def action(self):
        return self.view.application_url() + '/logout'
