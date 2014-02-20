# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grok
import sys

from fernlehrgang import Form
from dolmen.menu import menuentry
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.exports.menus import ExportItems
from fernlehrgang.lib.interfaces import IXLSExport
from zeam.form.base import Fields, action

from xlwt import Workbook
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, joinedload
from fernlehrgang import models
from fernlehrgang.browser.ergebnisse import CalculateResults
from fernlehrgang.exports.utils import page_query, makeZipFile, getUserEmail
from fernlehrgang.lib import nN


spalten = ('FLG_ID', 'TITEL FERNLEHRGANG', 'TEILNEHMER_ID', 'LEHRHEFT_ID', 'VERSANDANSCHRIFT', 'PLZ', 
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


def getXLSBases():
    book = Workbook()
    adressen = book.add_sheet('FLG-XLS Export')
    return book, adressen



def fd(v):
    if v == None:
        return ""
    try:
        return v.strftime('%d.%m.%Y')
    except:
        return v



def versandanschrift(teilnehmer):
    if teilnehmer.strasse != None or teilnehmer.nr != None or teilnehmer.plz != None or teilnehmer.ort != None:
        return "JA"
    return ""


def createSpalten(adressen):
    for i, spalte in enumerate(spalten):
        adressen.write(0, i, spalte)


def createRows(book, adressen, session, flg_id, lh_id, lh_nr, rdatum, stichtag):
    ii = 0 
    FERNLEHRGANG_ID = flg_id
    lehrhefte = session.query(models.Lehrheft).options(joinedload(models.Lehrheft.fragen)).filter(models.Lehrheft.fernlehrgang_id == FERNLEHRGANG_ID).all()
    result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).options(joinedload(models.Kursteilnehmer.antworten))
    result = result.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == FERNLEHRGANG_ID,
            models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
            models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
    i=1
    for teilnehmer, unternehmen, ktn in page_query(result):
        if ktn.status in ('A1', 'A2'):
            cal_res = CalculateResults(ktn)
            summary = cal_res.summary(lehrhefte)
            row = adressen.row(ii+1)
            row.write(0, nN(flg_id))
            row.write(1, nN(ktn.fernlehrgang.titel))
            row.write(2, nN(teilnehmer.id))
            row.write(3, lh_id)
            row.write(4, versandanschrift(teilnehmer))
            row.write(5, nN(teilnehmer.plz or unternehmen.plz))
            row.write(6, nN(unternehmen.mnr))
            row.write(7, nN(unternehmen.name))
            row.write(8, nN(unternehmen.name2))
            row.write(9, nN(teilnehmer.anrede))
            row.write(10, nN(teilnehmer.titel))
            row.write(11, nN(teilnehmer.vorname))
            row.write(12, nN(teilnehmer.name))
            row.write(13, fd(teilnehmer.geburtsdatum))
            strasse = nN(teilnehmer.strasse) + ' ' + nN(teilnehmer.nr)
            if strasse == " ":
                strasse = nN(unternehmen.str)
            else:
                if teilnehmer.adresszusatz:
                    strasse = strasse + ' // ' + teilnehmer.adresszusatz
            row.write(14, strasse)
            row.write(15, nN(teilnehmer.ort or unternehmen.ort))
            row.write(16, nN(teilnehmer.passwort))
            row.write(17, '') # Beliefart --> Leer laut Frau Esche 
            row.write(18, rdatum) # Variable
            row.write(20, summary.get('resultpoints')) # PUNKTZAHL --> Punktzahl der Rücksendungen
            row.write(21, stichtag) # Variable
            row.write(22, lh_nr) # LEHRHEFT --> Variable Für Welchen Ausdruck
            row.write(23, nN(teilnehmer.titel))
            row.write(24, nN(teilnehmer.vorname))
            row.write(25, nN(teilnehmer.name))
            z = 26 
            for lehrheft in lehrhefte:
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
            row.write(19, lhid) # RSENDUNG --> Anzahl der Rücksendung
            ii+=1


def export(session, flg_id, lh_id, lh, rdatum, stichtag, dateiname):
    """This should be the "shared" export function.
    """
    book, adressen = getXLSBases()
    createSpalten(adressen)
    createRows(book, adressen, session, flg_id, lh_id, lh, rdatum, stichtag)
    fn = "/tmp/%s" % dateiname
    xls_file = open(fn, 'w+')
    book.save(xls_file)
    xls_file.close()
    print "Writing File %s" % fn
    fn = makeZipFile(fn)
    return fn


@menuentry(ExportItems)
class XSLExportForm(Form):
    grok.context(IFernlehrgang)
    grok.title('Versandliste Fernlehrgang')

    fields = Fields(IXLSExport)

    @action(u"Export Starten")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Bitte korrigieren Sie die Fehler')
        from fernlehrgang.tasks import export_versandliste_fernlehrgang
        lh_id, lh = data['lehrheft'].split('-')
        mail = getUserEmail(self.request.principal.id)
        fn = export_versandliste_fernlehrgang.delay(self.context.id, lh_id, lh, data['rdatum'], data['stichtag'], data['dateiname'], mail) 
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
