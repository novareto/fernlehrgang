# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from dolmen.menu import menuentry
from fernlehrgang.config import POSTVERSANDSPERRE
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang.viewlets import NavigationMenu
from megrok.layout import Page


grok.templatedir('templates')


@menuentry(NavigationMenu)
class Resultate(Page):
    grok.context(IKursteilnehmer)
    grok.title('Ergebnisse')
    grok.name('resultate')

    title = u"Resultate"

    @property
    def description(self):
        teilnehmer = self.context.teilnehmer
        return u"Hier Können Sie die Resultate des Kursteilnehmers %s %s KTID %s einsehen." % (
                teilnehmer.name, teilnehmer.vorname, self.context.id)

    @property
    def getResults(self):
        results = ICalculateResults(self.context)
        return results.lehrhefte()

    @property
    def getSummary(self):
        results = ICalculateResults(self.context)
        return results.summary()


class CalculateResults(grok.Adapter):
    grok.implements(ICalculateResults)
    grok.context(IKursteilnehmer)

    def lehrhefte(self):
        context = self.context
        rc = []
        points = context.fernlehrgang.punktzahl
        for lehrheft in context.fernlehrgang.lehrhefte:
            res = {}
            res['titel'] = "%s - %s" %(lehrheft.nummer, lehrheft.titel)
            lehrheft_id = lehrheft.id
            fragen = []
            punkte = 0
            for antwort in context.antworten:
                if antwort.frage.lehrheft_id == lehrheft_id:
                    titel = "%s - %s" %(antwort.frage.frage, antwort.frage.titel)
                    ergebnis = self.calculateResult(antwort.antwortschema,
                                               antwort.frage.antwortschema,
                                               antwort.frage.gewichtung)
                    d=dict(titel = titel,
                           frage = antwort.frage.antwortschema,
                           antwort = antwort.antwortschema,
                           res = ergebnis)
                    punkte += ergebnis 
                    fragen.append(d)
            res['antworten'] = fragen
            res['punkte'] = punkte
            res['points'] = points
            rc.append(res)
        return rc

    def calculateResult(self, antworten, antwortschema, gewichtung):
        if len(antworten) != len(antwortschema):
            return 0
        antwortschema = list(antwortschema.lower())
        for x in antworten:
            if x.lower() not in antwortschema:
                return 0
        return gewichtung

    def summary(self):
        punkte = 0
        comment = "Nicht Bestanden"
        context = self.context
        mindest_punktzahl = context.fernlehrgang.punktzahl
        lehrhefte = self.lehrhefte()
        for lehrheft in lehrhefte:
            punkte += lehrheft['punkte']
        if context.status in POSTVERSANDSPERRE:
            comment = "Nicht Bestanden da Postversandsperre: %s" % context.status
        elif punkte >= mindest_punktzahl:
            comment = "Bestanden"
        return dict(points=mindest_punktzahl, resultpoints=punkte, comment=comment)
