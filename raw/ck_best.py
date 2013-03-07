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
sql = select(
    [teilnehmer, unternehmen, kursteilnehmer, antwort],
    and_(
        kursteilnehmer.c.fernlehrgang_id == FLG_ID, 
        kursteilnehmer.c.teilnehmer_id == teilnehmer.c.id,
        kursteilnehmer.c.id == antwort.c.kursteilnehmer_id,
        teilnehmer.c.unternehmen_mnr == unternehmen.c.MNR),
    use_labels=True,
    )


lhf_sql = select(
    [lehrheft, frage],
    and_(
        lehrheft.c.id == frage.c.lehrheft_id,
        lehrheft.c.fernlehrgang_id == FLG_ID
        ),
    use_labels=True,
    )


fragen = {}
lehrhefte = [] 


for row in session.execute(lhf_sql):
    if row.frage_id not in fragen.keys():
        fragen[row.frage_id] = row
    if row.lehrheft_id not in lehrhefte:
        lehrhefte.append(row.lehrheft_id)
        
    
pprint (fragen)
pprint (lehrhefte)


akt_teilnehmer = {}

for row in session.execute(sql):
    if row.kursteilnehmer_id not in akt_teilnehmer.keys():
        akt_teilnehmer[row.kursteilnehmer_id] = dict(
                t_name=row.teilnehmer_name,
                t_vorname=row.teilnehmer_vorname,
                u_name=row.adr_NAME1,
                t_id=row.teilnehmer_id,
                t_strasse=row.teilnehmer_strasse,
                t_nr=row.teilnehmer_nr,
                t_plz=row.teilnehmer_plz,
                t_ort=row.teilnehmer_ort,
                u_plz=row.adr_PLZ,
                u_mnr=row.adr_MNR,
                u_name2=row.adr_NAME2,
                antworten = []
                )
    akt_teilnehmer[row.kursteilnehmer_id]['antworten'].append( 
                    dict(a_id = row.antwort_id,
                         a_fr_id = row.antwort_frage_id,
                         a_system = row.antwort_system,
                         a_schema = row.antwort_antwortschema)
                    
                )
    

def calculateResult(antworten, antwortschema, gewichtung):
    if not antworten:
        return 0
    if not antwortschema:
        return 0
    if len(antworten) != len(antwortschema):
        return 0
    antwortschema = list(antwortschema.lower())
    for x in antworten:
        if x.lower() not in antwortschema:
            return 0
    return gewichtung


def versandanschrift(strasse, nr, plz, ort):
    if strasse != None or nr != None or plz != None or ort != None:
        return "JA"
    return ""


for t_id, teilnehmer in akt_teilnehmer.items():
    teilnehmer['lehrheft'] = []
    for antwort in teilnehmer['antworten']:
        lhs = {}
        frage = fragen.get(antwort['a_fr_id'])
        if frage.lehrheft_nummer not in lhs.keys():
            lhs[frage.lehrheft_nummer] = {'antworten':[], 'punkte':0, 'points':0} 
        erg = calculateResult(antwort['a_schema'], frage.frage_antwortschema, frage.frage_gewichtung)
        lhs[frage.lehrheft_nummer]['antworten'].append(dict(
            frage=frage.frage_antwortschema,
            antwort=antwort['a_schema'],
            system=antwort['a_system'],
            res = erg
            ))
        lhs[frage.lehrheft_nummer]['punkte'] += erg
    teilnehmer['lehrheft'].append(lhs)


pprint (akt_teilnehmer)
LH_ID=22
recs = []
for t_id, tn in akt_teilnehmer.items():
    liste = []
    liste.append(FLG_ID)
    liste.append(tn.get('t_id'))
    liste.append(LH_ID)
    liste.append(versandanschrift(tn.get('strasse'),tn.get('nr'),tn.get('plz'),tn.get('ort')))
    liste.append(tn.get('t_plz') or tn.get('u_plz'))
    liste.append(tn.get('u_mnr'))
    liste.append(tn.get('u_name'))
    liste.append(tn.get('u_nane2'))
    recs.append(liste)

print recs 
