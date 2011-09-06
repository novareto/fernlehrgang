# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grokcore.component as grok

from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.resultate import ICalculateResults
from xlwt import Workbook
from zope.interface import Interface
from zope.schema import *
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.saconfig import Session
from fernlehrgang import models



@grok.provider(IContextSourceBinder)
def lehrhefte(context):
    rc = []
    for lehrheft in context.lehrhefte:
        titel = "%s, %s" %(lehrheft.nummer, lehrheft.titel)
        key = "%s-%s" %(lehrheft.id, lehrheft.nummer)
        rc.append(SimpleTerm(key, key, titel))
    return SimpleVocabulary(rc)


class IXLSExport(Interface):
    """ xml export """

    dateiname = TextLine(
        title=u"Dateiname",
        description=u"Dateiname"
        )

    rdatum = TextLine(
        title=u"RDatum",
        description=u"RDatum"
        )

    stichtag = TextLine(
        title=u"Stichtag",
        description=u"Stichtag"
        )

    lehrheft = Choice(
        title=u"Lehrheft",
        description=u"Lehrheft",
        source = lehrhefte,
        )


    def createXLS():
        """ """



spalten = ('FLG_ID', 'TEILNEHMER_ID', 'LEHRHEFT_ID', 'PLZ', 'MITGLNRMIT', 'FIRMA', 'ANREDE', 'TITEL', 'VORNAME', 'NAME',
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



def nN(value):
    """ Not None"""
    if value == None:
        return ''
    return value

from profilehooks import profile


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

    def createRows(self, form):
        flg = self.context
        lh_id, lh_nr = form['lehrheft'].split('-')
        for i, ktn in enumerate(self.context.kursteilnehmer):
            cal_res = ICalculateResults(ktn)
            summary = cal_res.summary()
            row = self.adressen.row(i+1)
            teilnehmer = ktn.teilnehmer
            unternehmen = teilnehmer.unternehmen
            row.write(0, nN(flg.id))
            row.write(1, nN(teilnehmer.id))
            row.write(2, lh_id)
            row.write(3, nN(teilnehmer.plz or unternehmen.plz))
            row.write(4, nN(unternehmen.mnr))
            row.write(5, nN(unternehmen.name))
            row.write(6, nN(teilnehmer.anrede))
            row.write(7, nN(teilnehmer.titel))
            row.write(8, nN(teilnehmer.vorname))
            row.write(9, nN(teilnehmer.name))
            row.write(10, nN(teilnehmer.strasse) + ' ' + nN(teilnehmer.nr) or nN(unternehmen.str))
            row.write(11, nN(teilnehmer.ort or unternehmen.ort))
            row.write(12, nN(teilnehmer.passwort))
            row.write(13, '') # Beliefart --> Leer laut Frau Esche 
            row.write(14, form['rdatum']) # Variable
            row.write(16, summary.get('resultpoints')) # PUNKTZAHL --> Punktzahl der Rücksendungen
            row.write(17, form['stichtag']) # Variable
            row.write(18, lh_nr) # LEHRHEFT --> Variable Für Welchen Ausdruck
            row.write(19, nN(teilnehmer.titel))
            row.write(20, nN(teilnehmer.vorname))
            row.write(21, nN(teilnehmer.name))
            z = 22 
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
            for lhr in cal_res.lehrhefte():
                row.write(z, lhr.get('punkte'))
                z += 1
                if len(lhr['antworten']):
                   lhid = lhr['titel'].split('-')[0] 
            row.write(15, lhid) # RSENDUNG --> Anzahl der Rücksendung
            print i


    def createXLS(self, form):
        self.createSpalten()
        self.createRows(form)
        file = open('/tmp/adr.xls', 'w+')
        self.book.save(file)
        return file
