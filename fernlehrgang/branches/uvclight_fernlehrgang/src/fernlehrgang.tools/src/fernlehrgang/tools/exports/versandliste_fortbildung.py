# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import uvclight

from fernlehrgang.models.fernlehrgang import IFernlehrgang
from fernlehrgang.tools.exports.menus import ExportItems
from fernlehrgang.app.lib.interfaces import IXLSFortbildung
from openpyxl.workbook import Workbook
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from fernlehrgang import models
from fernlehrgang.app.browser.ergebnisse import CalculateResults
from fernlehrgang.app.lib import nN
from fernlehrgang.tools.exports.versandliste_fernlehrgang import versandanschrift
from fernlehrgang.tools.exports.utils import page_query, makeZipFile, getUserEmail


spalten = ['FLG_ID', 'TITEL FERNLEHRGANG', 'TEILNEHMER_ID', 'LEHRHEFT_ID', 'VERSANDANSCHRIFT', 'PLZ',
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


def getXLSBases():
    book = Workbook(optimized_write=True)
    adressen = book.create_sheet()
    rc = [spalten]
    return book, adressen, rc

def createRows(session, rc, flg_ids, stichtag):
    lhs = {}
    ids = [x for x in flg_ids]
    result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).options(joinedload(models.Kursteilnehmer.antworten))
    result = result.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id.in_(ids),
            models.Antwort.datum > stichtag,
            models.Antwort.kursteilnehmer_id == models.Kursteilnehmer.id,
            models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
            models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
    for x in ids:
        lehrhefte_sql = session.query(models.Lehrheft).options(joinedload(models.Lehrheft.fragen))
        lhs[x] = lehrhefte_sql.filter(models.Lehrheft.fernlehrgang_id == x).all()
    i=1
    for teilnehmer, unternehmen, ktn in page_query(result):
        if ktn.status in ('A1', 'A2'):
            cal_res = CalculateResults(ktn)
            summary = cal_res.summary(lhs[ktn.fernlehrgang_id])
            liste = []
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
                liste.append(nN(ktn.fernlehrgang.titel))
                liste.append(nN(teilnehmer.id))
                liste.append(nN(ktn.fernlehrgang.lehrhefte[0].id)) # IST IMMER NUR EINS DA--Fortbilding
                liste.append(nN(versandanschrift(teilnehmer)))
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
                rc.append(liste)
            i+=1



def export(session, flg_ids, stichtag):
    """This should be the "shared" export function.
    """
    book, adressen, rc = getXLSBases()
    flg_ids = [x for x in flg_ids]
    createRows(session, rc, flg_ids, stichtag)
    fn = "/tmp/fortbildung_%s.xlsx" % stichtag.strftime('%Y_%m_%d') 
    for z, line in enumerate(rc):
        adressen.append([cell for cell in line])
    print "Writing File %s" % fn
    book.save(fn)
    fn = makeZipFile(fn)
    return fn


@uvclight.menuentry(ExportItems)
class XLSFortbildung(uvclight.Form):
    uvclight.context(IFernlehrgang)
    uvclight.name('xlsfortbildung')
    uvclight.title(u'Versandliste Fortbildung')

    fields = uvclight.Fields(IXLSFortbildung)

    @uvclight.action(u"Export Starten")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Fehler beheben')
            return
        from fernlehrgang.tools.tasks import export_versandliste_fortbildung
        flg_ids = [x for x in data['fortbildungen']]
        mail = getUserEmail(self.request.principal.id)
        fn = export_versandliste_fortbildung.delay(flg_ids, data['stichtag'], mail)
        # fn = export_versandliste_fortbildung(flg_ids, data['stichtag'], mail)
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
