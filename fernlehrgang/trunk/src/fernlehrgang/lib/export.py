# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 
import time
import grokcore.component as grok

from sqlalchemy.orm import joinedload
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.resultate import ICalculateResults
from xlwt import Workbook
from zope.interface import Interface
from zope.schema import *
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.saconfig import Session
from fernlehrgang import models
from fernlehrgang import log
from sqlalchemy import and_
from fernlehrgang.lib.interfaces import IXLSExport
from fernlehrgang.lib import nN
from profilehooks import profile, timecall

from sqlalchemy.orm import class_mapper, defer
def defer_everything_but(entity, cols):
    m = class_mapper(entity)
    return [defer(k) for k in 
            set(p.key for p 
                in m.iterate_properties 
                if hasattr(p, 'columns')).difference(cols)]



spalten = ('FLG_ID', 'TEILNEHMER_ID', 'LEHRHEFT_ID', 'VERSANDANSCHRIFT', 'PLZ', 
    'MITGLNRMIT', 'FIRMA', 'FIRMA2', 'ANREDE', 'TITEL', 'VORNAME', 'NAME', 'GEBURTSDATUM',
    'STRASSE', 'WOHNORT', 'PASSWORT', 'BELIEFART', 'R_DATUM', 'RSENDUNG', 'PUNKTZAHL',
    'STICHTAG', 'LEHRHEFT', 'R_TITEL', 'R_VORNAME', 'R_NAME', 'L1_F_1', 'L1_F_2',
    'L1_F_3', 'L1_F_4', 'L1_F_5', 'L1_F_6', 'L1_F_7', 'L1_F_8', 'L1_F_9', 'L1_F_10',
    'L2_F_1', 'L2_F_2', 'L2_F_3', 'L2_F_4', 'L2_F_5', 'L2_F_6', 'L2_F_7', 'L2_F_8', 'L2_F_9',
    'L2_F_10', 'L3_F_1', 'L3_F_2', 'L3_F_3', 'L3_F_4', 'L3_F_5', 'L3_F_6', 'L3_F_7',
    'L3_F_8', 'L3_F_9', 'L3_F_10', 'L4_F_1', 'L4_F_2', 'L4_F_3', 'L4_F_4', 'L4_F_5',
    'L4_F_6', 'L4_F_7', 'L4_F_8', 'L4_F_9', 'L4_F_10','L5_F_1', 'L5_F_2', 'L5_F_3',
    'L5_F_4', 'L5_F_5', 'L5_F_6', 'L5_F_7', 'L5_F_8', 'L5_F_9', 'L5_F_10', 'L6_F_1',
    'L6_F_2', 'L6_F_3', 'L6_F_4', 'L6_F_5', 'L6_F_6', 'L6_F_7', 'L6_F_8', 'L6_F_9',
    'L6_F_10', 'L7_F_1', 'L7_F_2', 'L7_F_3', 'L7_F_4', 'L7_F_5', 'L7_F_6', 'L7_F_7',
    'L7_F_8', 'L7_F_9', 'L7_F_10', 'L8_F_1', 'L8_F_2', 'L8_F_3', 'L8_F_4', 'L8_F_5',
    'L8_F_6', 'L8_F_7', 'L8_F_8', 'L8_F_9', 'L8_F_10','L1_P', 'L2_P', 'L3_P',
    'L4_P', 'L5_P', 'L6_P', 'L7_P', 'L8_P', 'L9_P', 'L10_P', 'BDANZSDG', 'BDNR', 'BDGEWICHT',
    'BZANZSDG', 'BZANZBD', 'BDANFANG', 'BDENDE',
)


def fd(v):
    if v == None:
        return ""
    try:
        return v.strftime('%d.%m.%Y')
    except:
        return v

def page_query(q):
    offset = 0
    while True:
        r = False
        for a,b,c in q.limit(1000).offset(offset):
           r = True
           yield a,b,c 
        offset += 1000
        print offset
        if not r:
            break


class XLSExport(grok.Adapter):
    """ XML Export"""
    grok.implements(IXLSExport)
    grok.context(IFernlehrgang)

    def __init__(self, context):
        self.context = context
        self.book = Workbook()
        self.adressen = self.book.add_sheet('FLG-XLS Export')
         
    def createSpalten(self):
        for i, spalte in enumerate(spalten):
            self.adressen.write(0, i, spalte)

    def versandanschrift(self, teilnehmer):
        if teilnehmer.strasse != None or teilnehmer.nr != None or teilnehmer.plz != None or teilnehmer.ort != None:
            return "JA"
        return ""

    @profile
    def createRows(self, form):
        flg = self.context
        lh_id, lh_nr = form['lehrheft'].split('-')
        ii = 0 
        session = Session()
        FERNLEHRGANG_ID = flg.id
        lehrhefte = session.query(models.Lehrheft).options(joinedload(models.Lehrheft.fragen)).filter(models.Lehrheft.fernlehrgang_id == FERNLEHRGANG_ID).all()
        start = time.time()
        print "START", start
        result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).options(joinedload(models.Kursteilnehmer.antworten))
        result = result.filter(
            and_(
                models.Kursteilnehmer.fernlehrgang_id == FERNLEHRGANG_ID,
                models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
                models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
        res = time.time() - start
        print "CREATING SELECT", res
        i=1
        #result = result.all()
        res = time.time() - start
        print "FETCHING ALL", res
        for teilnehmer, unternehmen, ktn in page_query(result):
            if ktn.status in ('A1', 'A2'):
                cal_res = ICalculateResults(ktn)
                summary = cal_res.summary(lehrhefte)
                row = self.adressen.row(ii+1)
                row.write(0, nN(flg.id))
                row.write(1, nN(teilnehmer.id))
                row.write(2, lh_id)
                row.write(3, self.versandanschrift(teilnehmer))
                row.write(4, nN(teilnehmer.plz or unternehmen.plz))
                row.write(5, nN(unternehmen.mnr))
                row.write(6, nN(unternehmen.name))
                row.write(7, nN(unternehmen.name2))
                row.write(8, nN(teilnehmer.anrede))
                row.write(9, nN(teilnehmer.titel))
                row.write(10, nN(teilnehmer.vorname))
                row.write(11, nN(teilnehmer.name))
                row.write(12, fd(teilnehmer.geburtsdatum))
                strasse = nN(teilnehmer.strasse) + ' ' + nN(teilnehmer.nr)
                if strasse == " ":
                    strasse = nN(unternehmen.str)
                else:
                    if teilnehmer.adresszusatz:
                        strasse = strasse + ' // ' + teilnehmer.adresszusatz
                row.write(13, strasse)
                row.write(14, nN(teilnehmer.ort or unternehmen.ort))
                row.write(15, nN(teilnehmer.passwort))
                row.write(16, '') # Beliefart --> Leer laut Frau Esche 
                row.write(17, form['rdatum']) # Variable
                row.write(19, summary.get('resultpoints')) # PUNKTZAHL --> Punktzahl der Rücksendungen
                row.write(20, form['stichtag']) # Variable
                row.write(21, lh_nr) # LEHRHEFT --> Variable Für Welchen Ausdruck
                row.write(22, nN(teilnehmer.titel))
                row.write(23, nN(teilnehmer.vorname))
                row.write(24, nN(teilnehmer.name))
                z = 25 
                for lehrheft in flg.lehrhefte:
                    for frage in sorted(lehrheft.fragen, key=lambda frage: int(frage.frage)):
                        r=""
                        for antwort in ktn.antworten:
                            if frage.id == antwort.frage_id:
                                r = "%s\r %s\n %s\r" %(
                                        frage.antwortschema.upper(), 
                                        antwort.antwortschema, 
                                        cal_res.calculateResult(
                                            frage.antwortschema,
                                            antwort.antwortschema,
                                            frage.gewichtung))
                        row.write(z, r) 
                        z += 1
                lhid = ""        
                for lhr in cal_res.lehrhefte(lehrhefte):
                    row.write(z, lhr.get('punkte'))
                    z += 1
                    if len(lhr['antworten']):
                       lhid = lhr['titel'].split('-')[0] 
                row.write(18, lhid) # RSENDUNG --> Anzahl der Rücksendung
                log('Fernlehrgang Anzahl', ii)
                ii+=1
            else:
                log('STATUS', ktn.status)


    def createXLS(self, form):
        self.createSpalten()
        self.createRows(form)
        file = open('/tmp/fortbildung.xls', 'w+')
        self.book.save(file)
        return file


