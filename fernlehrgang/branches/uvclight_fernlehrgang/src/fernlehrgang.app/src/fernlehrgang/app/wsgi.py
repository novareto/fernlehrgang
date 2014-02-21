# -*- coding: utf-8 -*-

import os
import transaction

from uvclight.backends.patterns import TrajectLookup
from cromlech.browser import IPublicationRoot
from cromlech.browser import IRequest
from cromlech.configuration.utils import load_zcml
from cromlech.dawnlight import DawnlightPublisher, ViewLookup
from cromlech.dawnlight import view_locator, query_view
from cromlech.security import Interaction
from cromlech.security import unauthenticated_principal
from cromlech.sqlalchemy import create_and_register_engine, SQLAlchemySession
from cromlech.webob import request
from sqlalchemy_imageattach import context as store
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from webob.dec import wsgify
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import Interface, implementer, alsoProvides
from zope.location import Location
from zope.security.proxy import removeSecurityProxy

from .trajects import register_all
from .auth.handler import Benutzer
from .interfaces import IFernlehrgangApp
from fernlehrgang import models


class IFernlehrgangSkin(IRequest):
    pass


view_lookup = ViewLookup(view_locator(query_view))
model_lookup = TrajectLookup()


@implementer(IPublicationRoot, IFernlehrgangApp)
class Root(Location):

    def benutzer(self):
        return Benutzer

    def getSiteManager(self):
        return getGlobalSiteManager()


class Application(object):

    def __init__(self, store, engine):
        self.store = store
        self.engine = engine
        self.site = Root()
        self.publisher = DawnlightPublisher(
            model_lookup=model_lookup, view_lookup=view_lookup)

    @wsgify(RequestClass=request.Request)
    def __call__(self, request):
        with transaction.manager as tm:
            with SQLAlchemySession(self.engine, transaction_manager=tm):
                with Interaction(unauthenticated_principal):
                    # We apply the skin layer
                    alsoProvides(request, IFernlehrgangSkin)
                    
                    # Site and implicit context set up
                    setSite(self.site)
                    store.push_store_context(self.store)
    
                    # publish
                    result = self.publisher.publish(
                        request, self.site, handle_errors=True)

                    # Site and implicit context clean_up
                    setSite()
                    store.pop_store_context()

        return removeSecurityProxy(result)


def application_factory(global_conf, store_root, store_prefix, dsn):

    # read the zcml
    zcml_path = os.path.join(os.path.dirname(__file__), 'configure.zcml')
    load_zcml(zcml_path)

    # we register our Traject patterns for our lookup
    register_all(model_lookup.patterns)
    
    # We register our SQLengine under a given name
    engine = create_and_register_engine(dsn, 'fernlehrgang')
    engine.bind(models.Base)

    # We create it all
    metadata = models.Base.metadata
    metadata.create_all(engine.engine, checkfirst=True)

    # We now instanciate the Application
    # The name and engine are passed, to be used for the querying.
    fs_store = HttpExposedFileSystemStore(store_root, store_prefix)
    app = Application(fs_store, engine)

    return app
