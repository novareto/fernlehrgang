# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import uvclight
from sqlalchemy.orm import joinedload
from fernlehrgang.app.interfaces import IFernlehrgangApp
from fernlehrgang.models.teilnehmer import ITeilnehmer
from fernlehrgang.models.unternehmen import IUnternehmen
from fernlehrgang.models.kursteilnehmer import lieferstopps 
from fernlehrgang.models import Teilnehmer, Kursteilnehmer
from fernlehrgang.app.browser.viewlets import NavigationMenu
from fernlehrgang.models import ICalculateResults
from fernlehrgang.app.browser.widgets import fmtDate
from cromlech.sqlalchemy import get_session
from fernlehrgang.app.wsgi import model_lookup
from uvclight.backends.patterns import DefaultModel


@uvclight.menuentry(NavigationMenu, order=450)
class TeilnehmerSuche(uvclight.Form):
    uvclight.context(IFernlehrgangApp)
    uvclight.title(u'Statusabfrage Kurs Teilnehmer')
    uvclight.require('zope.View')
    uvclight.order(1500)

    template = uvclight.get_template('teilnehmersuche.cpt', __file__)

    label = u"Statusabfrage Teilnehmer."
    description = u"Bitte geben Sie die Kriterien ein um den Teilnehmer zu finden."

    fields = uvclight.Fields(ITeilnehmer).select('id', 'name', 'vorname', 'geburtsdatum') + uvclight.Fields(IUnternehmen).select('mnr')
    fields['id'].readonly = False
    fields['mnr'].readonly = False
    fields['name'].required = False
    fields['vorname'].required = False
    fields['geburtsdatum'].required = False

    results = []

    def getResults(self):
        root = grok.getSite()
        lfs = lieferstopps(None)
        for kursteilnehmer, item in self.results:
            model_lookup.patterns.locate(root, item, DefaultModel)
            model_lookup.patterns.locate(root, item.unternehmen, DefaultModel)
            results = {"comment": "Kein Fernlehrgang."}
            if kursteilnehmer.fernlehrgang:
                results = ICalculateResults(kursteilnehmer).summary()
                model_lookup.patterns.locate(root, kursteilnehmer, DefaultModel)            
                name = '<a href="%s"> %s </a>' % (self.url(kursteilnehmer), item.name)
                flg = kursteilnehmer.fernlehrgang
                model_lookup.patterns.locate(root, flg, DefaultModel)
                link_flg = '<a href="%s"> %s </a>' % (self.url(flg), flg.titel)
            else:
                name = '<a href="%s"> %s </a>' % (self.url(item), item.name)
                link_flg = "Kein Fernlehrgang"
            unternehmen = '<a href="%s"> %s </a>' % (self.url(item.unternehmen), item.unternehmen.name)
            gebdat = ""
            if item.geburtsdatum:
                gebdat = fmtDate(item.geburtsdatum)
            d = dict(name=name,
                     link_flg = link_flg,
                     gebdat = gebdat,
                     unternehmen = unternehmen,
                     vorname = item.vorname,
                     status = lfs.getTerm(kursteilnehmer.status).title,
                     bestanden = results['comment'])
            yield d

    @uvclight.action(u'Suchen')
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = get_session('fernlehrgang')
        #sql = session.query(Kursteilnehmer, Teilnehmer)
        sql = session.query(Kursteilnehmer, Teilnehmer).options(joinedload(Kursteilnehmer.antworten))
        sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        if data.get('id') != "":
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if data.get('name') != "":
            constraint = "%%%s%%" % data.get('name')
            sql = sql.filter(Teilnehmer.name.ilike(constraint))
            v = True
        if data.get('vorname') != "":
            constraint = "%%%s%%" % data.get('vorname')
            sql = sql.filter(Teilnehmer.vorname.ilike(constraint))
            v = True
        if data.get('mnr') != "":
            constraint = "%%%s%%" % data.get('mnr')
            sql = sql.filter(Teilnehmer.unternehmen_mnr.ilike(constraint))
            v = True
        #if data.get('mnr_g_alt') != "":
        #    constraint = "%%%s%%" % data.get('mnr_g_alt')
        #    sql = sql.filter(Teilnehmer.unternehmen.mnr_g_alt.ilike(constraint))
        #    v = True
        if data.get('geburtsdatum'):
            sql = sql.filter(Teilnehmer.geburtsdatum == data.get('geburtsdatum'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()
