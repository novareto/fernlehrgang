# -*- coding: utf-8 -*-

import os
import transaction

from uvclight import xmlrpc, sessionned
from uvclight.backends.sql import transaction_sql
from uvclight.backends.patterns import TrajectLookup

from cromlech.browser import IPublicationRoot
from cromlech.configuration.utils import load_zcml
from cromlech.dawnlight import DawnlightPublisher, ViewLookup
from cromlech.dawnlight import view_locator, query_view
from cromlech.security import Interaction
from cromlech.sqlalchemy import create_and_register_engine, SQLAlchemySession
from cromlech.webob.request import Request
from cromlech.i18n.utils import setLanguage

from sqlalchemy_imageattach import context as store
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore

from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import Interface, implementer, alsoProvides, Attribute
from zope.location import Location

from .trajects import register_all
from .auth.handler import USERS
from .interfaces import IFernlehrgangApp, IFernlehrgangSkin
from fernlehrgang import models
from uvclight.auth import secured, Principal


view_lookup = ViewLookup(view_locator(query_view))
model_lookup = TrajectLookup()


@implementer(IPublicationRoot, IFernlehrgangApp)
class Root(Location):

    def getSiteManager(self):
        return getGlobalSiteManager()


ROOT = Root()
PUBLISHER = DawnlightPublisher(
    model_lookup=model_lookup, view_lookup=view_lookup)



@implementer(IFernlehrgangApp)
class xmlrpc_factory(object):

    def __init__(self, global_conf, dsn):
        self.engine = create_and_register_engine(dsn, 'fernlehrgang')
        self.engine.bind(models.Base)
        self.handler = xmlrpc.XMLRPCApp(self, model_lookup)

    def __call__(self, environ, start_response):
        with SQLAlchemySession(self.engine):
            return self.handler(environ, start_response)


def application(fs_store, engine):

    @transaction_sql(engine)
    @sessionned('session.key')
    @secured(USERS, u"Please Login")
    def publish(environ, start_response):
        setLanguage('de')
        request = Request(environ)
        request.principal = Principal(
            environ['REMOTE_USER'], roles=['dolmen.content.Edit'])

        with Interaction(request.principal):
            with store.store_context(fs_store):
                setSite(ROOT)
                alsoProvides(request, IFernlehrgangSkin)
                response = PUBLISHER.publish(request, ROOT, handle_errors=True)
                setSite()

        return response(environ, start_response)

    return publish


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
    app = application(fs_store, engine)
    
    return fs_store.wsgi_middleware(app)
