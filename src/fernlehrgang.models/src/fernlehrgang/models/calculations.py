# -*- coding: utf-8 -*-

from zope.interface import implementer

from .lehrheft import Lehrheft
from .resultate import ICalculateResults
from .kursteilnehmer import IKursteilnehmer


POSTVERSANDSPERRE = ['L3', '94', '95']


def checkDate(date):
    if date:
        return date.strftime('%d.%m.%Y %H:%M')
    else:
        return ""


@implementer(ICalculateResults)
class KursteilnehmerResults(object):

    def __init__(self, kursteilnehmer):
        assert IKursteilnehmer.providedBy(kursteilnehmer)
        self.context = kursteilnehmer

    @staticmethod
    def _lehrhefte(context):
        raise NotImplementedError('Define your own query')

    def lehrhefte(self, lehrhefte=None):
        context = self.context
        rc = []
        points = context.fernlehrgang.punktzahl
        if not lehrhefte:
            lehrhefte =  self._lehrhefte(context)
        for lehrheft in sorted(lehrhefte, key=lambda lehrheft: lehrheft.nummer):
            res = {}
            res['titel'] = "%s - %s" %(lehrheft.nummer, lehrheft.titel)
            lehrheft_id = lehrheft.id
            fragen = []
            punkte = 0
            for antwort in context.antworten:
                if antwort.frage.lehrheft_id == lehrheft_id:
                    titel = "%s - %s" %(antwort.frage.frage, antwort.frage.titel)
                    ergebnis = self.calculateResult(
                        antwort.antwortschema,
                        antwort.frage.antwortschema,
                        antwort.frage.gewichtung)
                    d = dict(titel=titel,
                             frage=antwort.frage.antwortschema,
                             antwort=antwort.antwortschema,
                             system=antwort.system,
                             datum=checkDate(antwort.datum),
                             res=ergebnis)
                    punkte += ergebnis 
                    fragen.append(d)
            res['antworten'] = fragen
            res['punkte'] = punkte
            res['points'] = points
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

    def summary(self, lehrhefte=None):
        punkte = 0
        comment = "Nicht Bestanden (Punktzahl nicht erreicht)"
        context = self.context
        mindest_punktzahl = context.fernlehrgang.punktzahl
        lehrhefte = self.lehrhefte(lehrhefte)
        for lehrheft in lehrhefte:
            punkte += lehrheft['punkte']
        if context.status in POSTVERSANDSPERRE:
            comment = "Nicht Bestanden da Postversandsperre: %s" % context.status
        elif punkte >= mindest_punktzahl:
            comment = "Bestanden"
        # Abschlussgespräch Seminar
        if True:
            if context.branche == "ja":
                if context.un_klasse == 'G2':
                    if context.gespraech != '1':
                        comment = u'Nicht Bestanden, da das Abschlussseminar noch nicht erfolgreich abgeschlossen wurde.'
                if context.un_klasse == 'G3':
                    if context.gespraech != '1':
                        comment = u'Nicht Bestanden, da das Abschlussgespräch noch nicht erfolgreich absolviert wurde.'
            elif context.branche == "nein":
                if context.un_klasse == 'G2':
                    if context.gespraech != '1':
                        comment = u'Nicht Bestanden, da das Abschlussgespräch noch nicht erfolgreich absolviert wurde.'

        return dict(
            points=mindest_punktzahl, resultpoints=punkte, comment=comment)
