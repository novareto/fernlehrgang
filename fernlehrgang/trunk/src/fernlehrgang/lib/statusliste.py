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
from fernlehrgang.lib.interfaces import IXLSReport
from openpyxl.workbook import Workbook
from sqlalchemy import and_
from z3c.saconfig import Session


v_un_klasse = un_klasse(None)
v_gespraech = gespraech(None)


class XLSReport(grok.Adapter):
    """ XML Export"""
    grok.implements(IXLSReport)
    grok.provides(IXLSReport)
    grok.context(IFernlehrgang)
    spalten = ['TEILNEHMER_ID', 'Titel', 'Anrede', 'Name', 'Vorname', 'Geburtsdatum', 'Strasse', 'Hausnummer', 'PLZ', 'ORT',
        'Mitgliedsnummer', 'Unternehmen', ' ', ' ', 'Strasse', 'PLZ', 'Ort', 'Registriert', 'Kategorie', 'Lieferstopps',
        'Mitarbeiteranzahl', 'Branche (Schrotthandel etc..)', u'Abschlussgespräch', 'Status', 'Punktzahl',
        u'Antwortbögen']

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

    def createRows(self, form):
        flg = self.context
        session = Session()
        FERNLEHRGANG_ID = flg.id
        result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).filter(
            and_(
                models.Kursteilnehmer.fernlehrgang_id == FERNLEHRGANG_ID,
                models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
                models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id).all()
        i=1
        for teilnehmer, unternehmen, ktn in result:
            cal_res = ICalculateResults(ktn)
            summary = cal_res.summary()
            liste = []
            teilnehmer = ktn.teilnehmer
            antworten = len(ktn.antworten)/10
            if teilnehmer:
                gebdat = ""
                if teilnehmer.geburtsdatum:
                    gebdat = teilnehmer.geburtsdatum.strftime('%d.%m.%Y')
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
                liste.append(ktn.status)
                liste.append(self.un_helper(ktn.un_klasse))
                liste.append(nN(ktn.branche))
                liste.append(self.ges_helper(ktn.gespraech))
                liste.append(nN(summary['comment']))
                liste.append(nN(summary['resultpoints']))
                liste.append(antworten)
            self.rc.append(liste)
            i+=1

    def createXLS(self, form):
        self.createRows(form)
        for z, line in enumerate(self.rc):
            self.adressen.append([cell for cell in line])
        file = '/tmp/report.xls'
        self.book.save(file)
        return open(file, 'r')
