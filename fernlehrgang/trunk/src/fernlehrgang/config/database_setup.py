import grok 
from z3c.saconfig import EngineFactory, GloballyScopedSession 
from z3c.saconfig.interfaces import IEngineCreatedEvent 
from zope.app.appsetup.product import getProductConfiguration

config = getProductConfiguration('database')
DSN = config['dsn']
print DSN 
#DSN = 'oracle://flgprod:prodflg!@10.30.4.80/BGETest'

engine_factory = EngineFactory(DSN, convert_unicode=True, encoding='utf-8', optimize_limits=True, echo=False) 
scoped_session = GloballyScopedSession() 
 
grok.global_utility(engine_factory, direct=True) 
grok.global_utility(scoped_session, direct=True)
