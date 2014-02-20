# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from uvc.publication import WSGIApplication, LocalSite
from grokcore.site.interfaces import IApplication
from zope.authentication.interfaces import IAuthentication
from zope.component import getGlobalSiteManager
from zope.component.interfaces import ISite
from zope.interface import implementer
from zope.location import Location
from zope.pluggableauth import PluggableAuthentication
from zope.site.interfaces import IRootFolder


def setup_pau(registry):
    PAU = PluggableAuthentication()
    PAU.authenticatorPlugins = ('rdbauth', )
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")
    registry.registerUtility(PAU, IAuthentication, name=u'')
    

class Questionaries(LocalSite, WSGIApplication):
    pass


def application(global_conf, **local_conf):
    app = Questionaries(need_registry=True)
    registry = app.getSiteManager()
    setup_pau(registry)
    return app
