# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 


import grok

from fernlehrgang import log
from fernlehrgang import models
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import un_klasse, gespraech
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang.lib import nN
from fernlehrgang.lib.interfaces import IXLSFortbildung
from openpyxl.workbook import Workbook
from sqlalchemy import and_
from z3c.saconfig import Session


v_un_klasse = un_klasse(None)
v_gespraech = gespraech(None)


class XLSFortbildung(grok.Adapter):
    """ XML Export"""
    grok.implements(IXLSFortbildung)
    grok.provides(IXLSFortbildung)
    grok.context(IFernlehrgang)

    spalten = ['FLG_ID', 'TEILNEHMER_ID', 'LEHRHEFT_ID', 'VERSANDANSCHRIFT', 'PLZ',
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
        'BZANZSDG', 'BZANZBD', 'BDANFANG', 'BDENDE',] 

    def __init__(self, context):
        self.context = context
        self.book = Workbook(optimized_write=True)
        self.adressen = self.book.create_sheet()
        self.rc = [self.spalten]

    def createSpalten(self):
        for i, spalte in enumerate(self.spalten):
            self.adressen.write(0, i, spalte)

    def ges_helper(self, term):
        try:
            return v_gespraech.getTerm(term).title
        except:
            pass
        return ''

    def un_helper(self, term):
        try:
            return v_un_klasse.getTerm(term).title
        except:
            pass
        return ''

    def createRows(self, data):
        session = Session()
        ids = [x for x in data['fortbildungen']]
        result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).filter(
            and_(
                models.Kursteilnehmer.fernlehrgang_id.in_(ids),
                models.Antwort.datum > data['stichtag'],
                models.Antwort.kursteilnehmer_id == models.Kursteilnehmer.id,
                models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
                models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
        i=1
        print result.count()
        for teilnehmer, unternehmen, ktn in result.all():
            print i
            cal_res = ICalculateResults(ktn)
            summary = cal_res.summary()
            liste = []
            unternehmen = teilnehmer.unternehmen
            ss = set([x.lehrheft_id for x in ktn.antworten])
            antworten = len(ss)
            if teilnehmer and summary.get('resultpoints') >= 1:
                gebdat = ""
                if teilnehmer.geburtsdatum:
                    try:
                        gebdat = teilnehmer.geburtsdatum.strftime('%d.%m.%Y')
                    except:
                        gebdat = ""
                #unternehmen = teilnehmer.unternehmen
                liste.append(nN(ktn.fernlehrgang_id))
                liste.append(nN(teilnehmer.id))
                liste.append(nN(ktn.fernlehrgang.lehrhefte[0].id)) # IST IMMER NUR EINS DA--Fortbilding
                liste.append(nN(self.versandanschrift(teilnehmer)))
                liste.append(nN(teilnehmer.plz or unternehmen.plz))
                liste.append(nN(unternehmen.mnr))
                liste.append(nN(unternehmen.name))
                liste.append(nN(unternehmen.name2))
                liste.append(nN(teilnehmer.anrede))
                liste.append(nN(teilnehmer.titel))
                liste.append(nN(teilnehmer.vorname))
                liste.append(nN(teilnehmer.name))
                liste.append(nN(gebdat))
                strasse = nN(teilnehmer.strasse) + ' ' + nN(teilnehmer.nr)
                if strasse == " ":
                    strasse = nN(unternehmen.str)
                else:
                    if teilnehmer.adresszusatz:
                        strasse = strasse + ' // ' + teilnehmer.adresszusatz
                liste.append(nN(strasse))
                liste.append(nN(teilnehmer.ort or unternehmen.ort))
                liste.append(nN(teilnehmer.passwort))
                liste.append(' ')
                liste.append(' ') # RDATUM
                liste.append(' ') # ANZAHL 
                liste.append(nN(summary.get('resultpoints')))
                liste.append(nN(' ')) # STICHTAG
                liste.append(nN(ktn.fernlehrgang.lehrhefte[0].id))
                liste.append(nN(teilnehmer.titel))
                liste.append(nN(teilnehmer.vorname))
                liste.append(nN(teilnehmer.name))
                for lehrheft in ktn.fernlehrgang.lehrhefte:
                    for frage in sorted(lehrheft.fragen, key=lambda frage: int(frage.frage)):
                        r=""
                        for antwort in ktn.antworten:
                            if frage.id == antwort.frage_id:
                                r = "%s\r %s\n %s\r" %(
                                        frage.antwortschema.upper(),
                                        nN(antwort.antwortschema),
                                        cal_res.calculateResult(
                                            frage.antwortschema,
                                            antwort.antwortschema,
                                            frage.gewichtung))
                        liste.append(r)
            self.rc.append(liste)
            i+=1

    def versandanschrift(self, teilnehmer):
        if teilnehmer.strasse != None or teilnehmer.nr != None or teilnehmer.plz != None or teilnehmer.ort != None:
            return "JA"
        return ""

    def create(self, data):
        self.createRows(data)
        for z, line in enumerate(self.rc):
            self.adressen.append([cell for cell in line])
        file = '/tmp/fortbildung.xls'
        self.book.save(file)
        return open(file, 'r')
