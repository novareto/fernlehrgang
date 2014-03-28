# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


import json
import datetime
import uvclight

from sqlalchemy import *
from fernlehrgang.models import Frage, Teilnehmer, Antwort, Kursteilnehmer
from .interfaces import (
    ICalculateResults, ITeilnehmer, IKursteilnehmer, IFernlehrgangApp)


class TeilnehmerAPI(uvclight.REST):
    uvclight.context(ITeilnehmer)

    def GET(self):
        context = self.context
        kt_id = self.request.get('kt', None)
        branche = ""
        un_klasse = ""
        if kt_id:
            for ktn in context.kursteilnehmer:
                if ktn.id == int(kt_id):
                    branche = ktn.branche
                    un_klasse = ktn.un_klasse
        geburtsdatum = ""
        if context.geburtsdatum:
            geburtsdatum = context.geburtsdatum.strftime('%d.%m.%Y')
        teilnehmer = dict(
            anrede=context.anrede,
            titel=context.titel,
            vorname=context.vorname,
            name=context.name,
            geburtsdatum=geburtsdatum,
            strasse=context.strasse,
            nr=context.nr,
            plz=context.plz,
            ort=context.ort,
            email=context.email,
            un_klasse=un_klasse,
            branche=branche,
            kompetenzzentrum=context.kompetenzzentrum,
            )
        return json.dumps(teilnehmer)

    def PUT(self):
        teilnehmer = self.context
        data = json.loads(self.body)
        un_klasse = data.pop('un_klasse')
        branche = data.pop('branche')
        flg_id = data.pop('flg_id')
        data['geburtsdatum'] = datetime.datetime.strptime(data['geburtsdatum'], "%d.%m.%Y")
        for key, value in data.items():
            if value:
                setattr(teilnehmer, key, value)

        for ktm in teilnehmer.kursteilnehmer:
            if ktm.fernlehrgang_id == int(flg_id):
                ktm.un_klasse = un_klasse
                ktm.branche = branche
                ktm.status = "A1"
        return "1"


class KursteilnehmerAPI(uvclight.REST):
    uvclight.context(IKursteilnehmer)

    def GET(self):
        adapter = ICalculateResults(self.context)
        li = [adapter.summary(), adapter.lehrhefte()]
        return json.dumps(li)

    def PUT(self):
        kursteilnehmer = self.context
        data = json.loads(self.body)
        data['datum'] = datetime.datetime.strptime(data['datum'], "%d.%m.%Y")
        antwort = Antwort(**data)
        kursteilnehmer.antworten.append(antwort)
        return antwort.id
