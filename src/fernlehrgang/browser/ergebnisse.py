# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import json

from sqlalchemy.orm import joinedload
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.kursteilnehmer import IVLWKursteilnehmer
from fernlehrgang.interfaces.kursteilnehmer import IFortbildungKursteilnehmer
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang.viewlets import NavEntry
from fernlehrgang.browser import Page
from z3c.saconfig import Session
from fernlehrgang.models import Lehrheft


POSTVERSANDSPERRE = "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "S1", "Z1"


grok.templatedir("templates")


class ResNavEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.name("resnaventry")
    grok.order(50)

    title = "Ergebnisse"
    icon = "fas fa-chart-pie"

    def url(self):
        return self.view.url(self.context, "resultate")


class Resultate(Page):
    grok.context(IKursteilnehmer)
    grok.title("Ergebnisse")
    grok.name("resultate")

    title = "Resultate"

    @property
    def description(self):
        teilnehmer = self.context.teilnehmer
        return (
            "Hier Können Sie die Resultate des Kursteilnehmers %s %s KTID %s einsehen."
            % (teilnehmer.name, teilnehmer.vorname, self.context.id)
        )

    @property
    def getResults(self):
        results = ICalculateResults(self.context)
        return results.lehrhefte()

    @property
    def getSummary(self):
        results = ICalculateResults(self.context)
        return results.summary()


class ResultateVLW(Page):
    grok.context(IVLWKursteilnehmer)
    grok.title("Ergebnisse")
    grok.name("resultate")

    title = "Resultate"

    @property
    def description(self):
        teilnehmer = self.context.teilnehmer
        return (
            "Hier Können Sie die Resultate des Kursteilnehmers %s %s KTID %s einsehen."
            % (teilnehmer.name, teilnehmer.vorname, self.context.id)
        )

    @property
    def getSummary(self):
        results = ICalculateResults(self.context)
        return results.summary()

    def getAntwort(self):
        for antwort in self.context.antworten:
            if antwort.gbo:
                if antwort.gbo.upper().strip() == "OK":
                    return antwort
        return None

    def fmtJson(self, daten):
        return json.dumps(json.loads(daten), indent=4)


def checkDate(date):
    if date:
        return date.strftime("%d.%m.%Y %H:%M")
    else:
        return ""


class CalculateResults(grok.Adapter):
    grok.implements(ICalculateResults)
    grok.context(IKursteilnehmer)

    def lehrhefte(self, lehrhefte=None, session=None):
        context = self.context
        rc = []
        points = context.fernlehrgang.punktzahl
        if not lehrhefte:
            if not session:
                session = Session()
            sql = session.query(Lehrheft).options(joinedload(Lehrheft.fragen))
            sql = sql.filter(Lehrheft.fernlehrgang_id == context.fernlehrgang.id)
            lehrhefte = sql.all()
        for lehrheft in sorted(lehrhefte, key=lambda lehrheft: lehrheft.nummer):
            res = {}
            res["titel"] = "%s - %s" % (lehrheft.nummer, lehrheft.titel)
            lehrheft_id = lehrheft.id
            fragen = []
            punkte = 0
            # import pdb; pdb.set_trace()
            for antwort in sorted(
                context.antworten, key=lambda antwort: int(antwort.frage.frage)
            ):
                if antwort.frage.lehrheft_id == lehrheft_id:
                    titel = "%s - %s" % (antwort.frage.frage, antwort.frage.titel)
                    ergebnis = self.calculateResult(
                        antwort.antwortschema,
                        antwort.frage.antwortschema,
                        antwort.frage.gewichtung,
                    )
                    d = dict(
                        titel=titel,
                        frage=antwort.frage.antwortschema,
                        antwort=antwort.antwortschema,
                        system=antwort.system,
                        datum=checkDate(antwort.datum),
                        res=ergebnis,
                    )
                    punkte += ergebnis
                    fragen.append(d)
            res["antworten"] = fragen
            res["punkte"] = punkte
            res["points"] = points
            rc.append(res)
        return rc

    def calculateResult(self, antworten, antwortschema, gewichtung):
        if not antworten:
            return 0
        if not antwortschema:
            return 0
        if len(antworten) != len(antwortschema):
            return 0
        antwortschema = list(antwortschema.lower())
        for x in antworten:
            if x.lower() not in antwortschema:
                return 0
        return gewichtung

    def summary(self, lehrhefte=None, session=None, unternehmen=None):
        punkte = 0
        comment = "nicht bestanden (Punktzahl nicht erreicht)"
        context = self.context
        mindest_punktzahl = context.fernlehrgang.punktzahl
        lehrhefte = self.lehrhefte(lehrhefte, session)
        for lehrheft in lehrhefte:
            punkte += lehrheft["punkte"]
        if context.status in POSTVERSANDSPERRE:
            comment = "nicht bestanden da Postversandsperre: %s" % context.status
        elif punkte >= mindest_punktzahl:
            comment = "bestanden"
        c_punkte = " Punktzahl (%s/%s)" % (punkte, mindest_punktzahl)
        # Abschlussgespräch Seminar
        if not unternehmen:
            unternehmen = context.unternehmen
            branche = context.branche
            un_klasse = context.un_klasse
            if "nicht bestanden" not in comment:
                if branche == "ja":
                    if un_klasse == "G2" or un_klasse == "G":
                        if context.gespraech == "2":
                            # comment = u"nicht bestanden, da das Abschlussseminar nicht erfolgreich abgeschlossen wurde."
                            comment = "nicht bestanden (Seminar offen)"
                        elif context.gespraech == "0" or context.gespraech is None:
                            comment = "nicht bestanden (Seminar offen)"
                    if un_klasse == "G3":
                        if context.gespraech == "2":
                            # comment = u"nicht bestanden, da das Abschlussgespräch nicht erfolgreich absolviert wurde."
                            comment = "nicht bestanden (Abschlussgespräch offen)"
                        elif context.gespraech == "0" or context.gespraech is None:
                            comment = "nicht bestanden (Abschlussgespräch offen)"
                elif branche == "nein":
                    if un_klasse == "G2" or un_klasse == "G":
                        if context.gespraech == "2":
                            # comment = u"nicht bestanden, da das Abschlussgespräch nicht erfolgreich absolviert wurde."
                            comment = "nicht bestanden (Abschlussgespräch offen)"
                        elif context.gespraech == "0" or context.gespraech is None:
                            comment = "nicht bestanden (Abschlussgespräch offen)"
        self.context.fixed_results = comment
        if comment == "bestanden":
            klass = "text-success"
        else:
            klass = "text-danger"
        comment = "<b> <span class='%s'> %s </span> </b> %s" % (
            klass,
            comment,
            c_punkte,
        )
        # self.context._result = comment
        return dict(points=mindest_punktzahl, resultpoints=punkte, comment=comment)


class CalculateResultsFortbildung(CalculateResults):
    grok.implements(ICalculateResults)
    grok.context(IFortbildungKursteilnehmer)

    def summary(self, lehrhefte=None, session=None, unternehmen=None):
        punkte = 0
        comment = "nicht bestanden (Punktzahl nicht erreicht)"
        context = self.context
        mindest_punktzahl = context.fernlehrgang.punktzahl
        lehrhefte = self.lehrhefte(lehrhefte, session)
        for lehrheft in lehrhefte:
            punkte += lehrheft["punkte"]
        if context.status in POSTVERSANDSPERRE:
            comment = "nicht bestanden da Postversandsperre: %s" % context.status
        elif punkte >= mindest_punktzahl:
            comment = "bestanden"
        c_punkte = " Punktzahl (%s/%s)" % (punkte, mindest_punktzahl)
        # comment = "%s" %(comment, c_punkte)
        self.context.fixed_results = comment
        if comment.startswith("bestanden"):
            klass = "text-success"
        else:
            klass = "text-danger"
        comment = "<b> <span class='%s'> %s </span> </b> %s" % (
            klass,
            comment,
            c_punkte,
        )
        # self.context._result = comment
        return dict(points=mindest_punktzahl, resultpoints=punkte, comment=comment)


class CalculateResultsVLW(grok.Adapter):
    grok.implements(ICalculateResults)
    grok.context(IVLWKursteilnehmer)

    def lehrhefte(self, lehrhefte=None, session=None):
        return []

    def getResults(self):
        for antwort in self.context.antworten:
            if antwort.gbo and antwort.gbo.upper().strip() == "OK":
                return True
        return False

    def summary(self, lehrhefte=None, session=None, unternehmen=None):
        comment = "nicht bestanden (VLW noch nicht vollständig bearbeitet)"
        context = self.context
        if context.status in POSTVERSANDSPERRE:
            comment = "nicht bestanden"
        elif self.getResults():
            comment = "bestanden"
        branche = context.branche
        un_klasse = context.un_klasse
        if comment == "bestanden":
            if branche == "ja":
                if un_klasse == "G2" or un_klasse == "G1":
                    if context.gespraech == "2":
                        comment = "nicht bestanden (Seminar offen)"
                    elif context.gespraech == "0" or context.gespraech is None:
                        comment = "nicht bestanden (Seminar offen)"
                if un_klasse == "G3":
                    if context.gespraech == "2":
                        # comment = u"nicht bestanden, da das Abschlussgespräch noch nicht erfolgreich absolviert wurde."
                        comment = "nicht bestanden (Abschlussgespräch offen)"
                    elif context.gespraech == "0" or context.gespraech is None:
                        comment = "nicht bestanden (Abschlussgespräch offen)"
            elif branche == "nein":
                if un_klasse == "G2":
                    if context.gespraech == "2":
                        # comment = u"nicht bestanden, da das Abschlussgespräch noch nicht erfolgreich absolviert wurde."
                        comment = "nicht bestanden (Abschlussgespräch offen)"
                    elif context.gespraech == "0" or context.gespraech is None:
                        comment = "nicht bestanden (Abschlussgespräch offen)"
                elif un_klasse == "G1":
                    if context.gespraech == "2":
                        comment = "nicht bestanden (Seminar offen)"
                    elif context.gespraech == "0" or context.gespraech is None:
                        comment = "nicht bestanden (Seminar offen)"
        self.context.fixed_results = comment
        if comment == "bestanden":
            klass = "text-success"
        else:
            klass = "text-danger"
        comment = "<b> <span class='%s'> %s </span> </b> " % (klass, comment)
        return dict(points=0, resultpoints=0, comment=comment)
