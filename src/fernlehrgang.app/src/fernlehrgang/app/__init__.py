# -*- coding: utf-8 -*-

import grok
import logging

from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from zope.authentication.interfaces import IAuthentication
from zope.interface import Interface, implementer
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin

from .auth.handler import UserAuthenticatorPlugin
from .interfaces import IFernlehrgangApp


logger = logging.getLogger('fernlehrgang')


def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)


# SQLAlchemy LOGGING --> INFO for echo=True
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


def setup_pau(PAU):
    PAU.authenticatorPlugins = ('principals', )
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")


def image_middleware(app, config, root, prefix):
    fs_store = HttpExposedFileSystemStore(root, prefix)
    provideUtility(fs_store, Interface, name='ImageStore')
    return fs_store.wsgi_middleware(app)


@implementer(IFernlehrgangApp) 
class FernlehrgangApp(grok.Application, grok.Container):
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