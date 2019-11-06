# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang.browser import Form
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.exports.menus import ExportItems
from fernlehrgang.lib.interfaces import IXLSExport
from zeam.form.base import Fields, action

from xlwt import Workbook
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from fernlehrgang import models
from fernlehrgang.browser.ergebnisse import CalculateResults
from fernlehrgang.exports.utils import page_query, makeZipFile, getUserEmail
from fernlehrgang.lib import nN
from z3c.saconfig import Session
from fernlehrgang.lib.emailer import send_mail
from fernlehrgang.exports import q
from openpyxl.workbook import Workbook


spalten = [(
    'FLG_ID', 'TITEL FERNLEHRGANG', 'TEILNEHMER_ID',
    'VERSANDANSCHRIFT', 'PLZ', 'MITGLNRMIT', 'FIRMA', 'FIRMA2', 'ANREDE',
    'TITEL', 'VORNAME', 'NAME', 'GEBURTSDATUM', 'STRASSE', 'WOHNORT',
    'PASSWORT', 'R_VORNAME', 'R_NAME')]


def getXLSBases():
    book = Workbook(write_only=True)
    adressen = book.create_sheet()
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


def createRows(session, flg_id):
    spalten = []
    ii = 0 
    FERNLEHRGANG_ID = flg_id
    lehrhefte = session.query(models.Lehrheft).options(joinedload(models.Lehrheft.fragen)).filter(models.Lehrheft.fernlehrgang_id == FERNLEHRGANG_ID).order_by(models.Lehrheft.nummer).all()
    result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).options(joinedload(models.Kursteilnehmer.antworten))
    result = result.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == FERNLEHRGANG_ID,
            models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
            models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
    i=1
    for teilnehmer, unternehmen, ktn in page_query(result):
        if ktn.status in ('A1', 'A2'):
            row = []
            cal_res = CalculateResults(ktn)
            summary = cal_res.summary(lehrhefte)
            row.append(nN(flg_id))
            row.append(nN(ktn.fernlehrgang.titel))
            row.append(nN(teilnehmer.id))
            row.append(versandanschrift(teilnehmer))
            row.append(nN(teilnehmer.plz or unternehmen.plz))
            row.append(nN(unternehmen.mnr))
            row.append(nN(unternehmen.name))
            row.append(nN(unternehmen.name2))
            row.append(nN(teilnehmer.anrede))
            row.append(nN(teilnehmer.titel))
            row.append(nN(teilnehmer.vorname))
            row.append(nN(teilnehmer.name))
            row.append(fd(teilnehmer.geburtsdatum))
            strasse = nN(teilnehmer.strasse) + ' ' + nN(teilnehmer.nr)
            if strasse == " ":
                strasse = nN(unternehmen.str)
            else:
                if teilnehmer.adresszusatz:
                    strasse = strasse + ' // ' + teilnehmer.adresszusatz
            row.append(strasse)
            row.append(nN(teilnehmer.ort or unternehmen.ort))
            row.append(nN(teilnehmer.passwort))
            row.append(nN(teilnehmer.vorname))
            row.append(nN(teilnehmer.name))
            ii += 1
        spalten.append(row)
    return spalten


def export(flg_id, dateiname, mail):
    """This should be the "shared" export function.
    """
    session = Session()
    book, adressen = getXLSBases()
    mspalten = spalten + createRows(session, flg_id)
    if not dateiname.endswith('.xlsx'):
        dateiname += '.xlsx'
    for i, zeile in enumerate(mspalten):
        adressen.append(zeile)
    fn = "/tmp/%s" % dateiname
    book.save(fn)
    fn = makeZipFile(fn)
    text=u"Bitte öffen Sie die Datei im Anhang"
    import transaction
    with transaction.manager as tm:
        send_mail('flgapp@bghw.de', (mail,), "Fortbildung Datenquelle", text, [fn,])
    return fn


#@menuentry(ExportItems)
class XSLExportForm(Form):
    grok.context(IFernlehrgang)
    grok.title('Fortbildung - Einladungsschreiben')

    fields = Fields(IXLSExport).select('dateiname')

    @action(u"Export Starten")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Bitte korrigieren Sie die Fehler')
        flg_id = self.context.id
        #result = export(flg_id, data['dateiname'])
        try:
            mail = getUserEmail(self.request.principal.id)
        except:
            mail = "ck@novareto.de"
        #mail = "ck@novareto.de"
        result = q.enqueue_call(func=export, args=(flg_id, data['dateiname'], mail), timeout=12000)
        #result = export(flg_id, data['dateiname'], mail)
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
