# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grok

from dolmen.menu import menuentry
from fernlehrgang import models
from fernlehrgang.browser.ergebnisse import CalculateResults
from fernlehrgang.exports.menus import ExportItems
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.exports.versandliste_fortbildung import nN
from openpyxl.workbook import Workbook
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, joinedload
from fernlehrgang.interfaces.kursteilnehmer import un_klasse, gespraech
from fernlehrgang.exports.utils import page_query, makeZipFile, getUserEmail

import re
cleanr = re.compile('<.*?>')

def cleanhtml(raw_html):
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()


v_un_klasse = un_klasse(None)
v_gespraech = gespraech(None)

def nN(value):
    """ Not None"""
    if value == None:
        return ''
    if isinstance(value, int):
        return str(value)
    return value.replace('\x1a', '')


def ges_helper(term):
    try:
        return v_gespraech.getTerm(term).title
    except:
        pass
    return ''

def un_helper(term):
    try:
        return v_un_klasse.getTerm(term).title
    except:
        pass
    return ''


spalten = ['TEILNEHMER_ID', 'Titel', 'Anrede', 'Name', 'Vorname', 'Geburtsdatum', 'Strasse', 'Hausnummer', 'PLZ', 'ORT', 'EMail',
    'Mitgliedsnummer', 'Unternehmen', ' ', ' ', 'Strasse', 'PLZ', 'Ort', 'Registriert', 'Kategorie', 'Lieferstopps',
    'Mitarbeiteranzahl', 'Branche (Schrotthandel etc..)', u'Abschlussgespräch', 'Status', 'Punktzahl',
    u'Antwortbögen'
]


def getXLSBases():
    book = Workbook(write_only=True)
    adressen = book.create_sheet()
    rc = [spalten]
    return book, adressen, rc


def createRows(rc, session, flg_id):
    FERNLEHRGANG_ID = flg_id
    lehrhefte = session.query(models.Lehrheft).options(joinedload(models.Lehrheft.fragen)).filter(models.Lehrheft.fernlehrgang_id == FERNLEHRGANG_ID).all()
    result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).options(joinedload(models.Kursteilnehmer.antworten))
    result = result.filter(
        and_(
            models.Kursteilnehmer.fernlehrgang_id == FERNLEHRGANG_ID,
            models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
            models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
    print result.count()
    i=1
    for teilnehmer, unternehmen, ktn in page_query(result):
        if i in range(0,100000, 1000):
            print i
        cal_res = CalculateResults(ktn)
        summary = cal_res.summary(lehrhefte)
        liste = []
        teilnehmer = ktn.teilnehmer
        ss = set([x.rlhid for x in ktn.antworten])
        antworten = len(ss)
        if teilnehmer:
            gebdat = ""
            if teilnehmer.geburtsdatum:
                try:
                    gebdat = teilnehmer.geburtsdatum.strftime('%d.%m.%Y')
                except:
                    gebdat = ""
            #unternehmen = teilnehmer.unternehmen
            liste.append(nN(teilnehmer.id))
            liste.append(nN(teilnehmer.titel))
            liste.append(nN(teilnehmer.anrede))
            liste.append(nN(teilnehmer.name))
            liste.append(nN(teilnehmer.vorname))
            liste.append(gebdat)
            liste.append(nN(teilnehmer.strasse))
            liste.append(nN(teilnehmer.nr))
            liste.append(nN(teilnehmer.plz))
            liste.append(nN(teilnehmer.ort))
            liste.append(nN(teilnehmer.email))
            liste.append(nN(unternehmen.mnr))
            liste.append(nN(unternehmen.name))
            liste.append(nN(unternehmen.name2))
            liste.append(nN(unternehmen.name3))
            liste.append(nN(unternehmen.str))
            liste.append(nN(unternehmen.plz))
            liste.append(nN(unternehmen.ort))
 
            if teilnehmer.name:
                liste.append('ja')
            else:
                liste.append('nein')
            liste.append(nN(teilnehmer.kategorie))
            liste.append(nN(ktn.status))
            liste.append(un_helper(ktn.un_klasse))
            liste.append(nN(ktn.branche))
            liste.append(ges_helper(ktn.gespraech))
            liste.append(cleanhtml(nN(summary['comment'])))
            liste.append(nN(summary['resultpoints']))
            liste.append(nN(antworten))
        rc.append(liste)
        i+=1


from fernlehrgang.lib.emailer import send_mail
from fernlehrgang.exports import q
def export(flg_id, mail):
    """This should be the "shared" export function.
    """
    from z3c.saconfig import Session
    session = Session()
    fn = "/tmp/statusliste_%s.xlsx" % flg_id
    book, adressen, rc = getXLSBases()
    createRows(rc, session, flg_id)
    ws = adressen 
    for i, zeile in enumerate(rc):
        ws.append(zeile)
    book.save(fn)
    fn = makeZipFile(fn)
    text=u"Bitte öffen Sie die Datei im Anhang"
    import transaction
    with transaction.manager:
        send_mail('flgapp@bghw.de', (mail,), "Statusliste", text, [fn,])
    return fn


#@menuentry(ExportItems)
class XLSReport(grok.View):
    grok.context(IFernlehrgang)
    grok.name('xlsreport')
    grok.title('Statusliste')

    def update(self):
        mail = getUserEmail(self.request.principal.id)
        #fn = export(self.context.id, mail)
        fn = q.enqueue_call(func=export, args=(self.context.id, mail), timeout=6000)
        print fn

    def render(self):
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
