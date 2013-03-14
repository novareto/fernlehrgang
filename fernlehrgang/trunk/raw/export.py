from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import select, func
from sqlalchemy.sql import and_

engine = create_engine('oracle://cklinger:thaeyoo2@oracle/XE')

metadata = MetaData(bind=engine)
kursteilnehmer = Table('KURSTEILNEHMER', metadata, autoload=True, autoload_with=engine)
teilnehmer = Table('TEILNEHMER', metadata, autoload=True, autoload_with=engine)
unternehmen = Table('ADR', metadata, autoload=True, autoload_with=engine)
antwort = Table('ANTWORT', metadata, autoload=True, autoload_with=engine)


sql = select(
    [kursteilnehmer, teilnehmer, unternehmen, ], 
    and_(
        kursteilnehmer.c.fernlehrgang_id == 100, 
        kursteilnehmer.c.teilnehmer_id==teilnehmer.c.id, 
        teilnehmer.c.unternehmen_mnr==unternehmen.c.mnr),
    from_obj=[kursteilnehmer.outerjoin(antwort)]
    )

print sql
conn = engine.connect()
for x in conn.execute(sql).fetchall():
    import pdb; pdb.set_trace() 

