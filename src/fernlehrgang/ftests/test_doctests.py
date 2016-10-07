# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import fernlehrgang
import doctest
import unittest
import os

from zope.app.testing.functional import FunctionalDocFileSuite
from zope.app.testing.functional import ZCMLLayer


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
        #super(FLGZCMLLayer, self).testSetUp()
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


def test_suite():
    suite = unittest.TestSuite()
    functional = FunctionalDocFileSuite(
        'ftests/ablauf.txt', 'ftests/models.txt', 'ftests/vlw.txt',
        package="fernlehrgang",
        globs={'__name__': 'fernlehrgang'},
        optionflags=doctest.ELLIPSIS |
                    doctest.IGNORE_EXCEPTION_DETAIL |
                    doctest.REPORT_NDIFF |
                    doctest.NORMALIZE_WHITESPACE,
    )
    functional.layer = FunctionalLayer
    suite.addTest(functional)
    return suite
