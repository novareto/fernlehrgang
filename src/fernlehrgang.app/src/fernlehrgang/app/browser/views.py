# -*- coding: utf-8 -*-

import uvclight
from uvclight import Page, Index
from zope.interface import Interface, implementer
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from ..interfaces import IFernlehrgangApp
from uvc.design.canvas.views import IHomepage


class FaviconIco(uvclight.View):
    """ Helper for Favicon.ico Errors Request
    """
    uvclight.context(Interface)
    uvclight.name('favicon.ico')
    uvclight.require('zope.Public')

    def render(self):
        return "BLA"


@implementer(IHomepage)
class Index(Index):
    uvclight.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Testplattform Fernlehrgang"
    uvclight.require('zope.View')
    template = uvclight.get_template('index.cpt', __file__)
    

class Kontakt(Page):
    uvclight.context(Interface)
    uvclight.title(u"Kontakt")

    def render(self):
        return "KONTAKT"


class Logout(Page):
    uvclight.title('Abmelden')
    uvclight.context(Interface)
    uvclight.require('zope.Public')
    uvclight.order(200)

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
