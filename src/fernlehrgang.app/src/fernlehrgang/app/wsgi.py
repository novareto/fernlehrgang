# -*- coding: utf-8 -*-

import os
import transaction
import dawnlight

from uvclight import xmlrpc
from uvclight.backends.patterns import TrajectLookup
from webob.dec import wsgify

from cromlech.browser import IRequest, IPublicationRoot
from cromlech.configuration.utils import load_zcml
from cromlech.dawnlight import DawnlightPublisher, ViewLookup
from cromlech.dawnlight import view_locator, query_view
from cromlech.dawnlight.directives import traversable
from cromlech.security import Interaction
from cromlech.security import unauthenticated_principal
from cromlech.sqlalchemy import create_and_register_engine, SQLAlchemySession
from cromlech.webob import request
from cromlech.webob.request import Request
from cromlech.wsgistate import WsgistateSession
from cromlech.i18n.utils import setLanguage

from sqlalchemy_imageattach import context as store
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore

from zope.component import getMultiAdapter, getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import Interface, implementer, alsoProvides
from zope.location import Location
from zope.security.proxy import removeSecurityProxy

from .trajects import register_all
from .auth.handler import Benutzer, Users
from .interfaces import IFernlehrgangApp
from fernlehrgang import models
from uvclight.auth import secured, Principal
from uvc.themes.dguv import IDGUVRequest


class IFernlehrgangSkin(IDGUVRequest):
    pass


view_lookup = ViewLookup(view_locator(query_view))
model_lookup = TrajectLookup()


@implementer(IPublicationRoot, IFernlehrgangApp)
class Root(Location):

    def getSiteManager(self):
        return getGlobalSiteManager()


class UsersAuth(Users):

    def get(self, login, default=None):
        user = super(UsersAuth, self).get(login, default)
        if user:
            return user

    def getRoles(self, login):
        user = Users.get(self, login, None)
        if user:
            return [user.role]
        return []

Benutzer = UsersAuth()


@implementer(IFernlehrgangApp)
class xmlrpc_factory(object):

    def __init__(self, global_conf, dsn):
        self.engine = create_and_register_engine(dsn, 'fernlehrgang')
        self.engine.bind(models.Base)
        self.handler = xmlrpc.XMLRPCApp(self, model_lookup)

    def __call__(self, environ, start_response):
        with SQLAlchemySession(self.engine):
            return self.handler(environ, start_response)


class Application(object):

    def __init__(self, store, engine):
        self.store = store
        self.engine = engine
        self.site = Root()
        self.publisher = DawnlightPublisher(
            model_lookup=model_lookup, view_lookup=view_lookup)

    def __call__(self, environ, start_response):
        setLanguage('de-DE')
        request = Request(environ)

        @secured(Benutzer, "PLEASE Login")
        def publish(environ, start_response):
            #roles = Benutzer.getRoles('gbleeck')
            request.principal = Principal(environ['REMOTE_USER'])
            with Interaction(request.principal):
                with store.store_context(self.store):
                    setSite(self.site)
                    alsoProvides(request, IFernlehrgangSkin)
                    response = self.publisher.publish(
                        request, self.site, handle_errors=True)
                    setSite()
            return response(environ, start_response)

        with transaction.manager as tm:
            with SQLAlchemySession(self.engine, transaction_manager=tm):
                with WsgistateSession(environ, 'session.key'):
                    return publish(environ, start_response)


def application_factory(global_conf, store_root, store_prefix, dsn):

    # read the zcml
    zcml_path = os.path.join(os.path.dirname(__file__), 'configure.zcml')
    load_zcml(zcml_path)

    # We register our SQLengine under a given name
    engine = create_and_register_engine(dsn, 'fernlehrgang')
    engine.bind(models.Base)

    # we register our Traject patterns for our lookup
    register_all(model_lookup)
    
    # We create it all
    metadata = models.Base.metadata
    metadata.create_all(engine.engine, checkfirst=True)

    # We now instanciate the Application
    # The name and engine are passed, to be used for the querying.
    fs_store = HttpExposedFileSystemStore(store_root, store_prefix)
    app = Application(fs_store, engine)

    return fs_store.wsgi_middleware(app)
