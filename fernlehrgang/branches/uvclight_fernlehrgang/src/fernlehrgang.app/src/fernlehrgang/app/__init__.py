# -*- coding: utf-8 -*-

import grok
import logging

from uvc.publication import WSGIApplication, LocalSite
from grokcore.site.interfaces import IApplication
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from zope.authentication.interfaces import IAuthentication
from zope.component import provideUtility
from zope.component.interfaces import ISite
from zope.interface import Interface, implementer
from zope.pluggableauth import PluggableAuthentication
from .auth.handler import Benutzer
from .interfaces import IFernlehrgangApp


logger = logging.getLogger('fernlehrgang')


def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)


# SQLAlchemy LOGGING --> INFO for echo=True
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


def setup_pau(registry):
    PAU = PluggableAuthentication()
    PAU.authenticatorPlugins = ('Benutzer', )
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")
    registry.registerUtility(PAU, IAuthentication, name=u'')


def image_middleware(app, config, root, prefix):
    fs_store = HttpExposedFileSystemStore(root, prefix)
    provideUtility(fs_store, Interface, name='ImageStore')
    return fs_store.wsgi_middleware(app)


@implementer(IFernlehrgangApp) 
class FernlehrgangApp(LocalSite, WSGIApplication):
    grok.traversable(attr='benutzer')

    def benutzer(self):
        return Benutzer


def application(global_conf, **local_conf):
    app = FernlehrgangApp(need_registry=True)
    registry = app.getSiteManager()
    setup_pau(registry)
    return app
