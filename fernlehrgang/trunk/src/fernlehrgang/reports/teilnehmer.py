# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
import uvc.layout

from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.kursteilnehmer import lieferstopps 
from fernlehrgang.models import Teilnehmer, Kursteilnehmer
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import action, NO_VALUE, Fields
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang import Form


grok.templatedir('templates')


@menuentry(NavigationMenu, order=500)
class CreateTeilnehmer(Form):
    grok.context(IFernlehrgangApp)
    grok.title(u'Teilnehmer registrieren')
    title = label = u"Teilnehmer registrieren"
    description = u"Bitte geben Sie die Teilnehmer ID ein, den Sie registrieren möchten."
    results = []

    cssClasses = {'table': 'tablesorter myTable'}

    fields = Fields(ITeilnehmer).select('id')
    fields['id'].readonly = False

    @action(u'Suchen')
    def handle_search(self):
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Teilnehmer)
        sql = sql.filter(Teilnehmer.id == data.get('id'))
        teilnehmer = sql.first()
        if teilnehmer:
            site = grok.getSite()
            locate(site, teilnehmer, DefaultModel)
            self.redirect(self.url(teilnehmer, 'edit'))
        else:
            self.flash('Es wurde kein Teilnehmer gefunden')


@menuentry(NavigationMenu, order=450)
class TeilnehmerSuche(Form):
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage KursTeilnehmer')
    grok.require('zope.View')
    grok.order(1500)

    label = u"Statusabfrage Teilnehmer."
    description = u"Bitte geben Sie die Kriterien ein um den Teilnehmer zu finden."

    fields = Fields(ITeilnehmer).select('id', 'name', 'vorname', 'geburtsdatum') + Fields(IUnternehmen).select('mnr')
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
            locate(root, item, DefaultModel)
            locate(root, item.unternehmen, DefaultModel)
            results = {"comment": "Kein Fernlehrgang."}
            if kursteilnehmer.fernlehrgang:
                results = ICalculateResults(kursteilnehmer).summary()
                locate(root, kursteilnehmer, DefaultModel)            
                name = '<a href="%s"> %s </a>' % (self.url(kursteilnehmer), item.name)
                flg = kursteilnehmer.fernlehrgang
                locate(root, flg, DefaultModel)
                link_flg = '<a href="%s"> %s </a>' % (self.url(flg), flg.titel)
            else:
                name = '<a href="%s"> %s </a>' % (self.url(item), item.name)
                link_flg = "Kein Fernlehrgang"
            unternehmen = '<a href="%s"> %s </a>' % (self.url(item.unternehmen), item.unternehmen.name)
            gebdat = ""
            if item.geburtsdatum:
                gebdat = item.geburtsdatum.strftime('%d.%m.%Y')
            d = dict(name=name,
                     link_flg = link_flg,
                     gebdat = gebdat,
                     unternehmen = unternehmen,
                     vorname = item.vorname,
                     status = lfs.getTerm(kursteilnehmer.status).title,
                     bestanden = results['comment'])
            yield d

    @action(u'Suchen')
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Kursteilnehmer, Teilnehmer)
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
        if data.get('geburtsdatum') != NO_VALUE:
            sql = sql.filter(Teilnehmer.geburtsdatum == data.get('geburtsdatum'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()
