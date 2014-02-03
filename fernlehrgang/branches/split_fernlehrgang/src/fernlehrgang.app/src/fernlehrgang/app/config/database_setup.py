# -*- coding: utf-8 -*-

import grok 
from z3c.saconfig import EngineFactory, GloballyScopedSession 
from z3c.saconfig.interfaces import IEngineCreatedEvent 
from zope.app.appsetup.product import getProductConfiguration


config = getProductConfiguration('database')
DSN = config['dsn']

engine_factory = EngineFactory(
    DSN, convert_unicode=True, encoding='utf-8', echo=False) 
scoped_session = GloballyScopedSession() 
 
grok.global_utility(engine_factory, direct=True) 
grok.global_utility(scoped_session, direct=True)
