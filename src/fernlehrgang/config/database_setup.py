import grok 
from z3c.saconfig import EngineFactory, GloballyScopedSession 
from z3c.saconfig.interfaces import IEngineCreatedEvent 
 
#DSN = 'postgres://cklinger@localhost:5432/fernlehrgang' 
#DSN = 'oracle://flg:flg@192.168.2.104/XE'
DSN = 'oracle://novareto:retonova@10.30.4.80/BGETest'
#DSN = 'mysql://root:thasake39@localhost/fernlehrgang'

engine_factory = EngineFactory(DSN, echo=False, convert_unicode=False, encoding='utf-8') 
scoped_session = GloballyScopedSession() 
 
grok.global_utility(engine_factory, direct=True) 
grok.global_utility(scoped_session, direct=True)
