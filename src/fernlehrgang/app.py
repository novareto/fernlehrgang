# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from z3c.saconfig import Session
from megrok.traject import locate
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from zope.interface import Interface
#from uvc.layout.interfaces import IFooter, IPersonalPreferences
from grokcore.layout import Page
#from megrok import navigation
#from uvc.entities.interfaces import IFooter

from fernlehrgang.auth.handler import UserAuthenticatorPlugin
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.authentication.interfaces import IAuthentication
from zeam.form.ztk.widgets.date import DateWidgetExtractor, DateFieldWidget
from zope.i18n.format import DateTimeParseError
from zeam.form.base import NO_VALUE
from zope.component import getUtility
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from uvc.menus.components import MenuItem
from zeam.form.ztk import customize
from zope.schema.interfaces import IDate
from fernlehrgang import fmtDate
from zeam.form.ztk.widgets.date import DateFieldWidget, DateFieldDisplayWidget
from zeam.form.base.markers import NO_VALUE
from zope.error.error import RootErrorReportingUtility
from zope.error.interfaces import IErrorReportingUtility
from megrok.nozodb import ApplicationRoot
from grokcore.content.interfaces import IContext
from zope.pluggableauth import PluggableAuthentication


class ErrorUtility(RootErrorReportingUtility, grok.GlobalUtility):
    grok.provides(IErrorReportingUtility)


grok.templatedir('templates')


class PAU(PluggableAuthentication, grok.GlobalUtility):
    grok.provides(IAuthentication)
#    grok.name('pau')

    def __init__(self, *args, **kwargs):
        super(PAU, self).__init__(*args, **kwargs)
        self.authenticatorPlugins = ('principals', )
        self.credentialsPlugins = ("cookies", "No Challenge if Authenticated")


class FernlehrgangApp(ApplicationRoot):
    grok.implements(IFernlehrgangApp, IContext)
    grok.traversable('app')

    def get(self, key):
        return None

    def app(self):
        return grok.getSite()


grok.global_utility(
    UserAuthenticatorPlugin, provides=IAuthenticatorPlugin,
    name='principals',
    )


class Index(Page):
    grok.context(IFernlehrgangApp)
    grok.baseclass()
    title = u"Fernlehrgang"
    description = u"Testplattform Fernlehrgang"
    grok.require('zope.View')


#class KontaktMI(MenuItem):
#    grok.context(Interface)
#    grok.title(u"Kontakt")
#    grok.viewletmanager(IFooter)
#
#    @property
#    def action(self):
#        return "/kontakt"
#        return self.view.application_url() + '/kontakt'


class Kontakt(Page):
    grok.context(Interface)
    grok.title(u"Kontakt")

    def render(self):
        return "KONTAKT"


class RestLayer(grok.IRESTLayer):
    """ Layer for Rest Access"""
    grok.restskin('api')


class KPTZLayer(grok.IRESTLayer):
    """ Layer for Rest Access"""
    grok.restskin('kptz')



#@customize(origin=IDate)
#def customize_size(field):
#    field.valueLength = 'medium'


class DateFieldWidget(DateFieldWidget):

    def valueToUnicode(self, value):
        return fmtDate(value)


class DateFieldDisplayWidget(DateFieldDisplayWidget):

    def valueToUnicode(self, value):
        return fmtDate(value)


class NotFound(Page, grok.components.NotFoundView):
    """Not Found Error View
    """
    def application_url(self, *args, **kwargs):
        return ""


class SystemError(grok.components.ExceptionView):
    """Custom System Error for UVCSITE
    """

    def __init__(self, context, request):
        super(SystemError, self).__init__(context, request)
        self.context = grok.getSite()
        self.origin_context = context

    def update(self):
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'text/html')


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





class HAProxyStatus(grok.View):
    grok.context(Interface)
    grok.name('haproxycheck')
    grok.require('zope.Public')

    def render(self):
        from z3c.saconfig import Session
        session = Session()
        flg = session.query(Fernlehrgang).get(100)
        if flg:
            return "OK"
        return "NOT OK"
