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
from megrok.layout import Page
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


class Index(models.Index):
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
        return self.view.application_url() + 'kontakt'


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
        return self.view.application_url() + 'logout'


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


class Favicon(grok.View):
    """ Helper for Favicon.ico Errors Request
    """
    grok.context(Interface)
    grok.name('favicon.ico')
    grok.require('zope.Public')

    def render(self):
        return "BLA"


#class ExtraInfo(grok.ViewletManager):
#    grok.implements(IExtraInfo)
#    grok.name('uvc.layout.extrainfo')
#    grok.context(Interface)


class CustomDateFieldWidget(DateFieldWidget):
    """ Extractor for German Date Notation
    """

    def valueToUnicode(self, value):
        locale = self.request.locale
        formatter = locale.dates.getFormatter(self.valueType, 'medium')
        return formatter.format(value)


class CustomDateWidgetExtractor(DateWidgetExtractor):
    """ Extractor for German Date Notation
    """

    def extract(self):
        value, error = super(DateWidgetExtractor, self).extract()
        if value is not NO_VALUE:
            locale = self.request.locale
            formatter = locale.dates.getFormatter(self.valueType, 'medium')
            try:
                value = formatter.parse(value)
            except (ValueError, DateTimeParseError), error:
                return None, u"Bitte überprüfen Sie das Datumsformat. (tt.mm.jjjj)"
        return value, error
