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

    def createRows(self, data):
        session = Session()
        ids = [x for x in data['fortbildungen']]
        result = session.query(models.Teilnehmer, models.Kursteilnehmer, models.Unternehmen).filter(
            and_(
                models.Kursteilnehmer.fernlehrgang_id.in_(ids),
                models.Antwort.datum > data['stichtag'],
                models.Antwort.kursteilnehmer_id == models.Kursteilnehmer.id,
                models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
                models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr)).order_by(models.Teilnehmer.id)
        print result.count()
        for x, y, z in result.all():
            print x, y, z
            print "-"*55

    def create(self, data):
        self.createRows(data)
        #for z, line in enumerate(self.rc):
        #    self.adressen.append([cell for cell in line])
        #file = '/tmp/report.xls'
        #self.book.save(file)
        #return open(file, 'r')
