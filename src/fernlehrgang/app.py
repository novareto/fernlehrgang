# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from z3c.saconfig import Session
from megrok.traject import locate
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from dolmen.app.layout import models
from zope.interface import Interface
from dolmen.menu import menuentry
from uvc.layout.interfaces import IFooter, IExtraInfo, IPersonalPreferences
from uvc.layout import Page
#from megrok import navigation

from fernlehrgang.auth.handler import UserAuthenticatorPlugin
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.authentication.interfaces import IAuthentication
from zeam.form.ztk.widgets.date import DateWidgetExtractor, DateFieldWidget
from zope.i18n.format import DateTimeParseError
from zeam.form.base import NO_VALUE
from zope.component import getUtility
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from uvc.layout import MenuItem
from zeam.form.ztk import customize
from zope.schema.interfaces import IDate
from fernlehrgang import fmtDate


grok.templatedir('templates')


def setup_pau(PAU):
    PAU.authenticatorPlugins = ('principals', )
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")


class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp)
    grok.traversable(attr='benutzer')

    grok.local_utility(
        UserAuthenticatorPlugin, provides=IAuthenticatorPlugin,
        name='principals',
        )

    grok.local_utility(
        PluggableAuthentication,
        provides=IAuthentication,
        public=True,
        setup=setup_pau,
        )

    def benutzer(self):
        return getUtility(IAuthenticatorPlugin, 'principals').user_folder


class Index(Page):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Testplattform Fernlehrgang"
    grok.require('zope.View')


class KontaktMI(MenuItem):
    grok.context(Interface)
    grok.title(u"Kontakt")
    grok.viewletmanager(IFooter)

    @property
    def action(self):
        return "/kontakt"
        return self.view.application_url() + '/kontakt'


class Kontakt(Page):
    grok.context(Interface)
    grok.title(u"Kontakt")

    def render(self):
        return "KONTAKT"


class LogoutMI(MenuItem):
    grok.context(Interface)
    grok.title(u"Abmelden")
    grok.viewletmanager(IPersonalPreferences)

    @property
    def action(self):
        return "/kontakt"
        return self.view.application_url() + '/logout'


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


class RestLayer(grok.IRESTLayer):
    """ Layer for Rest Access"""
    grok.restskin('api')


class KPTZLayer(grok.IRESTLayer):
    """ Layer for Rest Access"""
    grok.restskin('kptz')



@customize(origin=IDate)
def customize_size(field):
    field.valueLength = 'medium'




from zeam.form.ztk.widgets.date import DateFieldWidget, DateFieldDisplayWidget
from zeam.form.base.markers import NO_VALUE


class DateFieldWidget(DateFieldWidget):

    def valueToUnicode(self, value):
        return fmtDate(value)


class DateFieldDisplayWidget(DateFieldDisplayWidget):

    def valueToUnicode(self, value):
        return fmtDate(value)


class NotFound(Page, grok.components.NotFoundView):
    """Not Found Error View
    """
    pass


class SystemError(Page, grok.components.ExceptionView):
    """Custom System Error for UVCSITE
    """

    def __init__(self, context, request):
        super(SystemError, self).__init__(context, request)
        self.context = grok.getSite()
        self.origin_context = context


class FaviconIco(grok.View):
    """ Helper for Favicon.ico Errors Request
    """
    grok.context(Interface)
    grok.name('favicon.ico')
    grok.require('zope.Public')

    def render(self):
        return "BLA"


from zope.i18n.interfaces import IUserPreferredLanguages
from zope.publisher.interfaces.http import IHTTPRequest

class GermanBrowserLangugage(grok.Adapter):
    grok.context(IHTTPRequest)
    grok.implements(IUserPreferredLanguages)

    def getPreferredLanguages(self):
        return ['de', 'de-de']


from uvc.layout.interfaces import IHeaders
class TestSystem(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def update(self):
        from zope.app.appsetup.product import getProductConfiguration
        config = getProductConfiguration('database')
        DSN = config['dsn']
        if DSN.startswith('oracle://novareto:retonova@10.30.131.206/BGETest'):
            if hasattr(self.view, 'flash'):
                self.view.flash(u"Test - System", type="info")
            else:
                print self.view

    def render(self):
        return ""
