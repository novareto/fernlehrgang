# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import grok

from fernlehrgang import log
from z3c.saconfig import EngineFactory, GloballyScopedSession
from zope.app.appsetup.product import getProductConfiguration

import logging

config = getProductConfiguration('database')
try:
    DSN = config['dsn']
except:
    DSN = "postgresql+psycopg2://flg:flg@localhost/flg"
log(DSN)


import logging
logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


# FIX: engine_factory = EngineFactory(DSN, convert_unicode=True, encoding='utf-8', optimize_limits=True, echo=False)
engine_factory = EngineFactory(
    DSN, convert_unicode=False, encoding='utf-8', echo=False, pool_recycle=60)
scoped_session = GloballyScopedSession()

grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)
