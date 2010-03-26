# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from megrok.traject import locate
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields
from dolmen.app.layout import models
from zope.interface import Interface
from dolmen.menu import menuentry
from uvc.layout.interfaces import IFooter
from megrok.layout import Page

from uvc.auth.auth import UserAuthenticatorPlugin, setup_authentication
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin


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
    description = u"Beschreibugn Fernlehrgang"
    grok.require('zope.View')


@menuentry(IFooter)
class Kontakt(Page):
    grok.context(Interface)
    grok.title(u"Kontakt")

    def render(self):
        return "KONTAKT"
