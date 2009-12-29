import grok 
from z3c.saconfig import EngineFactory, GloballyScopedSession 
from z3c.saconfig.interfaces import IEngineCreatedEvent 
 
DSN = 'postgres://cklinger@localhost:5432/fernlehrgang' 
 
engine_factory = EngineFactory(DSN, convert_unicode=True, echo=False) 
scoped_session = GloballyScopedSession() 
 
grok.global_utility(engine_factory, direct=True) 
grok.global_utility(scoped_session, direct=True)
