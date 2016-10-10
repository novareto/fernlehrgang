# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import fernlehrgang
import doctest
import unittest
import os

from zope.app.testing.functional import ZCMLLayer

import gocept.httpserverlayer.wsgi
import gocept.httpserverlayer.zopeappwsgi
import zope.app.appsetup.testlayer

from StringIO import StringIO
import copy
import plone.testing
import zope.app.appsetup.product


pc = """
<product-config database>
    DSN sqlite://
    SCHEMA
</product-config>

<product-config mailer>
    queue-path /Users/ck/work/bghw/fernlehrgang/var/mailer-queue
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


class FLGZCMLLayer(ZCMLLayer):

    def testSetUp(self):
        from z3c.saconfig import Session
        session = Session()
        from fernlehrgang.models import Base
        mt = Base.metadata
        mt.bind = session.connection().engine
        mt.create_all()

    def testTearDown(self):
        from fernlehrgang.models import Base
        mt = Base.metadata
        mt.drop_all()

FunctionalLayer = FLGZCMLLayer(
    ftesting_zcml, __name__,
    'FunctionalLayer',
    allow_teardown=True,
    product_config=pc,
)

from z3c.saconfig import Session
class ProductConfigLayer(plone.testing.Layer):

    def __init__(self, product_config, **kw):
        super(ProductConfigLayer, self).__init__(**kw)
        self.product_config = product_config

    def setUp(self):
        self['old_product_config'] = copy.deepcopy(
            zope.app.appsetup.product.saveConfiguration())
        self['product_config'] = zope.app.appsetup.product.loadConfiguration(
            StringIO(self.product_config))
        self.testSetUp()

    def testSetUp(self):
        # Create a copy so tests can modify it as they please.
       zope.app.appsetup.product.restoreConfiguration(
           copy.deepcopy(self['product_config']))

    def tearDown(self):
        del self['product_config']
        zope.app.appsetup.product.restoreConfiguration(
            self['old_product_config'])
        del self['old_product_config']


ZODB_LAYER = zope.app.appsetup.testlayer.ZODBLayer(
   fernlehrgang, ftesting_zcml)


class WSGILayer(gocept.httpserverlayer.zopeappwsgi.Layer):

    defaultBases = (ZODB_LAYER,)

    def get_current_zodb(self):
        return ZODB_LAYER.db

WSGI_LAYER = WSGILayer()

HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))


PRODUCT_LAYER = ProductConfigLayer(pc)


class AppLayer(plone.testing.Layer):
    defaultBases = (PRODUCT_LAYER, HTTP_LAYER)


APP_LAYER = AppLayer()

APP_LAYER = plone.testing.Layer((PRODUCT_LAYER, HTTP_LAYER), name="app_layer")

#def test_suite():
#    suite = unittest.TestSuite()
#    functional = FunctionalDocFileGSuite(
#        'ftests/ablauf.txt', 'ftests/models.txt', 'ftests/vlw.txt', # 'ftests/accept.txt',
#        package="fernlehrgang",
#        globs={'__name__': 'fernlehrgang'},
#        optionflags=doctest.ELLIPSIS |
#                    doctest.IGNORE_EXCEPTION_DETAIL |
#                    doctest.REPORT_NDIFF |
#                    doctest.NORMALIZE_WHITESPACE,
#    )
#    functional.layer = APP_LAYER 
#    suite.addTest(functional)
#    return suite

from zope.testing import doctestcase
from z3c.saconfig import Session


@doctestcase.doctestfiles('vlw.txt', 'ablauf.txt', 'models.txt', optionflags=doctest.ELLIPSIS)
class MoreTests(unittest.TestCase):
    layer = APP_LAYER

    def setUp(self):
        self.globs = {'getRootFolder': ZODB_LAYER.getRootFolder }
        self.session = Session()
        from fernlehrgang.models import Base
        mt = Base.metadata
        mt.bind = self.session.connection().engine
        mt.create_all(checkfirst=True)

    def VVVVtestSetUp(self):
        print "testSetUp"
        from fernlehrgang.models import Base
        mt = Base.metadata
        mt.bind = self.session.connection().engine
        mt.create_all(checkfirst=True)

    def tearDown(self):
        print "TEAR DOWN"
        from fernlehrgang.models import Base
        meta = Base.metadata
        meta.bind = self.session.connection().engine
        meta.drop_all()

#        with contextlib.closing(self.session.connection()) as con:
#            trans = con.begin()
#            for table in reversed(meta.sorted_tables):
#                con.execute(table.delete())
#            trans.commit()



#@doctestcase.doctestfiles('vlw.txt', optionflags=doctest.ELLIPSIS)
#class MoreTests11(unittest.TestCase):
#    layer = APP_LAYER
#    def setUp(self):
#        self.globs = {'getRootFolder': ZODB_LAYER.getRootFolder }

