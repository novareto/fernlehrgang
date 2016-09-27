# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import grok

from fernlehrgang import log
from z3c.saconfig import EngineFactory, GloballyScopedSession
from zope.app.appsetup.product import getProductConfiguration

config = getProductConfiguration('database')
try:
    DSN = config['dsn']
except:
    DSN = "postgresql+psycopg2://flg:flg@localhost/flg"
log(DSN)


print DSN

# FIX: engine_factory = EngineFactory(DSN, convert_unicode=True, encoding='utf-8', optimize_limits=True, echo=False)
engine_factory = EngineFactory(
    DSN, convert_unicode=True, encoding='iso-8859-15', echo=False)
scoped_session = GloballyScopedSession()

grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)
