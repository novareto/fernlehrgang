# -*- coding: utf-8 -*-

import grok
from dolmen.app.layout import models
from megrok.layout import Page
from zope.interface import Interface
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from ..interfaces import IFernlehrgangApp

grok.templatedir('templates')


class FaviconIco(grok.View):
    """ Helper for Favicon.ico Errors Request
    """
    grok.context(Interface)
    grok.name('favicon.ico')
    grok.require('zope.Public')

    def render(self):
        return "BLA"


class Index(models.Index):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Testplattform Fernlehrgang"
    grok.require('zope.View')


class Kontakt(Page):
    grok.context(Interface)
    grok.title(u"Kontakt")

    def render(self):
        return "KONTAKT"


class Logout(Page):
    grok.title('Abmelden')
    grok.context(Interface)
    grok.require('zope.Public')
    grok.order(200)

    KEYS = ("beaker.session.id", "dolmen.authcookie", "auth_pubtkt")

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            for key in self.KEYS:
                self.request.response.expireCookie(key,
                path='/', domain="bg-kooperation.de")
        else:
            self.request.response.expireCookie("auth_pubtkt",
                path='/', domain="bg-kooperation.de")

    def render(self):
        return self.redirect(self.application_url() + '/login')
