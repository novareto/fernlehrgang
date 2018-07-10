# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import ZODB.ActivityMonitor
import ZODB.interfaces
import doctest
import fernlehrgang
import gocept.httpserverlayer.wsgi
import gocept.httpserverlayer.zopeappwsgi
import os
import transaction
import unittest

from z3c.saconfig import Session
from zope import component
from zope.app.appsetup.testlayer import createTestDB
from zope.app.publication.zopepublication import ZopePublication
from zope.app.testing.functional import FunctionalTestSetup
from zope.testing import doctestcase


pc = """
<product-config database>
    DSN sqlite://
    SCHEMA
</product-config>

<product-config mailer>
    queue-path /tmp/mailer-queue
    hostname localhost
    port 25
    username
    password
</product-config>
"""

ftesting_zcml = os.path.join(
    os.path.dirname(fernlehrgang.__file__),
    'ftesting.zcml',
)


class ZODBLayer(object):
    """This layer load a ZCML configuration and create a test database.

    You can access the test database with layer.getRootFolder().
    """
    db = None
    db_name = 'main'
    connection = None
    __bases__ = tuple()
    
    def __init__(self, config_file, module, name, allow_teardown=False,
                 product_config=None):
        self.config_file = config_file
        self.__module__ = module
        self.__name__ = name
        self.allow_teardown = allow_teardown
        self.product_config = product_config
    
    def getRootFolder(self):
        """This return the root object of the database or assert if
        the database have not been created yet.
        """
        if self.connection is None:
            assert self.db is not None
            self.connection = self.db.open()
        return self.connection.root()[ZopePublication.root_name]

    def _close_db(self):
        # Close any opened connections
        if self.connection is not None:
            transaction.abort()
            self.connection.close()
            self.connection = None

        # Close the Database
        if self.db is not None:
            base = component.getGlobalSiteManager()
            base.unregisterUtility(
                self.db, ZODB.interfaces.IDatabase, self.db_name)
            self.db.close()
            self.db = None

    def setUp(self):
        self.setup = FunctionalTestSetup(
            self.config_file, product_config=self.product_config)
        self.db = createTestDB(self.db_name)
        self.base_storage = self.db._storage
        self._base_db_open = True

    def testSetUp(self):
        from fernlehrgang.models import Base
        session = Session()
        Base.metadata.create_all(session.connection().engine)
        transaction.commit()
        if self._base_db_open:
            self._close_db()
            self._base_db_open = False
        self.db = createTestDB(self.db_name, self.base_storage)

    def testTearDown(self):
        self._close_db()
        from fernlehrgang.models import Base
        session = Session()
        Base.metadata.drop_all(session.connection().engine)
        transaction.commit()
        session.close()

    def tearDown(self):
        self.setup.tearDownCompletely()
        if not self.allow_teardown:
            raise NotImplementedError


LAYER = ZODBLayer(ftesting_zcml, "fernlehrgang", 'layer', product_config=pc)


class WSGILayer(gocept.httpserverlayer.zopeappwsgi.Layer):

    defaultBases = (LAYER,)

    def get_current_zodb(self):
        return LAYER.db


HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGILayer(),))


@doctestcase.doctestfiles(
    'models.txt', 'vlw.txt', 'ablauf.txt', 'results.txt', 'importcheck.txt', optionflags=doctest.ELLIPSIS)
class MoreTests(unittest.TestCase):
    layer = HTTP_LAYER

    def setUp(self):
        self.globs = {'getRootFolder': LAYER.getRootFolder }
        self.session = Session()
