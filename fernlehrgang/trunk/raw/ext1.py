# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

from fernlehrgang.models import Frage, Fernlehrgang, Kursteilnehmer, Teilnehmer, Unternehmen, Antwort, Lehrheft 
from z3c.saconfig import Session
from sqlalchemy import select, and_
from pprint import pprint

session = Session()

#Getting the Table
kursteilnehmer = Kursteilnehmer.__table__
teilnehmer = Teilnehmer.__table__
unternehmen = Unternehmen.__table__
antwort = Antwort.__table__
lehrheft = Lehrheft.__table__
fernlehrgang = Fernlehrgang.__table__
frage = Frage.__table__

FLG_ID = 100

flg_sql = select([fernlehrgang.c.punktzahl], fernlehrgang.c.id == FLG_ID)
flg_points = session.execute(flg_sql).fetchone()[0]

lehrhefte_sql = select([lehrheft], lehrheft.c.fernlehrgang_id == FLG_ID)
lehrhefte = session.execute(lehrhefte_sql).fetchall()



sql = select(
    [kursteilnehmer, teilnehmer, unternehmen], 
    and_(
        kursteilnehmer.c.fernlehrgang_id == FLG_ID, 
        kursteilnehmer.c.teilnehmer_id==teilnehmer.c.id, 
        teilnehmer.c.unternehmen_mnr==unternehmen.c.MNR),
    use_labels=True,
    )

print sql



rc = {} 




for row in session.execute(sql):
    print row.kursteilnehmer_id, row.teilnehmer_name, row.teilnehmer_vorname
    fa_sql = select([frage, antwort, lehrheft],
            and_(frage.c.id == antwort.c.frage_id,
                 antwort.c.kursteilnehmer_id == row.kursteilnehmer_id,
                 lehrheft.c.id == frage.c.lehrheft_id), use_labels=True
            ).order_by(lehrheft.c.nummer)
    for x in session.execute(fa_sql).fetchall():
        res = {'antworten': []}
        res['titel'] = "%s - %s" %(x.lehrheft_nummer, x.lehrheft_titel)
        import pdb; pdb.set_trace() 
        res['antworten'].append(x.frage_titel)

print res

