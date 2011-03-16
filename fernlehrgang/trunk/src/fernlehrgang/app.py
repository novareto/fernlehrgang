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
from uvc.layout.interfaces import IFooter, IExtraInfo
from megrok.layout import Page

from uvc.auth.auth import UserAuthenticatorPlugin, setup_authentication
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.authentication.interfaces import IAuthentication
from zeam.form.ztk.widgets.date import DateWidgetExtractor, DateFieldWidget
from zope.i18n.format import DateTimeParseError
from zeam.form.base import NO_VALUE


grok.templatedir('templates')


class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp) 
    grok.local_utility(
        UserAuthenticatorPlugin, provides=IAuthenticatorPlugin,
        name='users',
        )
    grok.local_utility(
        PluggableAuthentication, provides=IAuthentication,
        setup=setup_authentication,
        )


class Index(models.Index):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Testplattform Fernlehrgang"
    grok.require('zope.View')


@menuentry(IFooter)
class Kontakt(Page):
    grok.context(Interface)
    grok.title(u"Kontakt")

    def render(self):
        return "KONTAKT"



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


class ExtraInfo(grok.ViewletManager):
    grok.implements(IExtraInfo)
    grok.name('uvc.layout.extrainfo')
    grok.context(Interface)


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

