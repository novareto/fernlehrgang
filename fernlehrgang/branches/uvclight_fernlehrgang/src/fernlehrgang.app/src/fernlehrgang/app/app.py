# -*- coding: utf-8 -*-

import grok
import logging
import transaction
from webob.dec import wsgify
from cromlech.dawnlight import DawnlightPublisher
from zope.security.proxy import removeSecurityProxy
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from zope.interface import Interface, implementer
from cromlech.sqlalchemy import SQLAlchemySession
from cromlech.security import Interaction
from zope.component.hooks import setSite
from sqlalchemy_imageattach import context as store
from cromlech.browser import IPublicationRoot

from .auth.handler import Benutzer
from .interfaces import IFernlehrgangApp
from fernlehrgang import models

logger = logging.getLogger('fernlehrgang')


def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)


# SQLAlchemy LOGGING --> INFO for echo=True
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)



@implementer(IPublicationRoot, IFernlehrgangApp)
class FernlehrgangApp(object):
    grok.traversable(attr='benutzer')

    def benutzer(self):
        return Benutzer

    def getSiteManager(self):
        return getGlobalSiteManager()


class Application(object):

    def __init__(self, root, engine):
        self.engine = engine
        self.site = FernlehrgangApp()
        self.publisher = DawnlightPublisher(view_lookup=view_lookup)
        self.fs_store = HttpExposedFileSystemStore(root, prefix)
        
    @wsgify(RequestClass=request.Request)
    def __call__(self, request):
        with SQLAlchemySession(self.engine):
            with transaction.manager:
                with Interaction():
                    # Site and implicit context set up
                    setSite(self.site)
                    store.push_store_context(self.fs_store)
    
                    # publish
                    result = self.publisher.publish(
                        request, self.site, handle_errors=True)

                    # Site and implicit context clean_up
                    setSite()
                    store.pop_store_context()

                    return removeSecurityProxy(result)


def application_factory(global_conf, root, dsn, **kwargs):

    # We register our SQLengine under a given name
    engine = create_and_register_engine(dsn, 'fernlehrgang')
    metadata = models.Base.metadata
    metadata.create_all(engine, checkfirst=True)

    # We bind out SQLAlchemy definition to the engine
    engine.bind(Library)

    # We now instanciate the TrajectApplication
    # The name and engine are passed, to be used for the querying.
    app = Application(root, engine)

    return app
