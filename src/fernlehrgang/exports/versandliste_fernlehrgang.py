# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang import Form
from dolmen.menu import menuentry
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


spalten = (
    'FLG_ID', 'TITEL FERNLEHRGANG', 'TEILNEHMER_ID',
    'VERSANDANSCHRIFT', 'PLZ', 'MITGLNRMIT', 'FIRMA', 'FIRMA2', 'ANREDE',
    'TITEL', 'VORNAME', 'NAME', 'GEBURTSDATUM', 'STRASSE', 'WOHNORT',
    'PASSWORT', 'STICHTAG', 'R_VORNAME', 'R_NAME')


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


def createRows(book, adressen, session, flg_id):
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
            cal_res = CalculateResults(ktn)
            summary = cal_res.summary(lehrhefte)
            row = adressen.row(ii+1)
            row.write(0, nN(flg_id))
            row.write(1, nN(ktn.fernlehrgang.titel))
            row.write(2, nN(teilnehmer.id))
            row.write(3, versandanschrift(teilnehmer))
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
            row.write(16, nN(teilnehmer.vorname))
            row.write(17, nN(teilnehmer.name))
            ii += 1


def export(flg_id, dateiname, mail):
    """This should be the "shared" export function.
    """
    session = Session()
    book, adressen = getXLSBases()
    createSpalten(adressen)
    createRows(book, adressen, session, flg_id)
    fn = "/tmp/%s" % dateiname
    xls_file = open(fn, 'w+')
    book.save(xls_file)
    xls_file.close()
    fn = makeZipFile(fn)
    text=u"Bitte öffen Sie die Datei im Anhang"
    import transaction
    with transaction.manager as tm:
        send_mail('flgapp@bghw.de', (mail,), "Fortbildung Datenquelle", text, [fn,])
    return fn


@menuentry(ExportItems)
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
        result = q.enqueue_call(func=export, args=(flg_id, data['dateiname'], mail), timeout=600)
        #result = export(flg_id, data['dateiname'], mail)
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
