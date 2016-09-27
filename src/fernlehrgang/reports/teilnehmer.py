# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

# from profilehooks import profile
from sqlalchemy.orm import joinedload
from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer 
from fernlehrgang.models import Teilnehmer, Kursteilnehmer
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import action, Fields
from fernlehrgang.interfaces.resultate import ICalculateResults
from fernlehrgang import Form
from fernlehrgang import fmtDate
from fernlehrgang.interfaces.search import ISearch
from fernlehrgang.resources import chosen_js, chosen_css, chosen_ajax
from grokcore.chameleon.components import ChameleonPageTemplateFile


grok.templatedir('templates')


@menuentry(NavigationMenu, order=-100)
class TeilnehmerSuche(Form):
    grok.name('index')
    grok.context(IFernlehrgangApp)
    grok.title(u'Statusabfrage KursTeilnehmer')
    grok.require('zope.View')
    grok.order(1500)

    label = u"Statusabfrage Teilnehmer."
    description = u"Bitte geben Sie die Kriterien ein \
    um den Teilnehmer zu finden."

    fields = Fields(ISearch).select('id')
    fields['id'].title = u"Teilnehmer"
    fields['id'].description = u"Hier können Sie einen Teilnehmer suchen."

    results = None 

    def update(self):
        chosen_js.need()
        chosen_css.need()
        chosen_ajax.need()

    def updateWidgets(self):
        super(TeilnehmerSuche, self).updateWidgets()
        field_id = self.fieldWidgets.get('form.field.id')
        field_id.template = ChameleonPageTemplateFile('templates/select.cpt')

    def getResults(self):
        root = grok.getSite()
        lfs = lieferstopps(None)
        for kursteilnehmer, item in self.results:
            locate(root, item, DefaultModel)
            results = {"comment": "Kein Fernlehrgang."}
            if kursteilnehmer.fernlehrgang:
                results = ICalculateResults(kursteilnehmer).summary()
                locate(root, kursteilnehmer, DefaultModel)
                name = '<a href="%s"> %s </a>' % (
                    self.url(kursteilnehmer), item.name)
                name = item.name
                link_ktn = '<a href="%s"> <span class="glyphicon glyphicon-user" aria-hidden="true"></span> </a>' % (
                    self.url(kursteilnehmer))
                link_tn = '<a href="%s"> <span class="glyphicon glyphicon-user" aria-hidden="true"></span> </a>' % (
                    self.url(kursteilnehmer.teilnehmer))
                flg = kursteilnehmer.fernlehrgang
                locate(root, flg, DefaultModel)
                link_flg = '<a href="%s"> %s </a>' % (self.url(flg), flg.titel)
            else:
                name = '<a href="%s"> %s </a>' % (self.url(item), item.name)
                link_flg = "Kein Fernlehrgang"
            rcu = []
            for unt in item.unternehmen:
                locate(root, unt, DefaultModel)
                res = ICalculateResults(
                    kursteilnehmer).summary(unternehmen=unt)
                rcu.append('<a href="%s"> %s (%s) </a>' % (
                    self.url(unt), unt.name, res['comment']))
            gebdat = ""
            if item.geburtsdatum:
                gebdat = fmtDate(item.geburtsdatum)
            je = []
            for j in item.journal_entries:
                je.append(
                    dict(
                        status=j.status,
                        datum=j.date.strftime("%d.%m.%Y"),
                        info=j.type
                        ))
            d = dict(name=name,
                     link_flg=link_flg,
                     gebdat=gebdat,
                     link_ktn=link_ktn,
                     link_tn=link_tn,
                     titel=ITeilnehmer.get('titel').source.getTermByToken(
                         item.titel).title,
                     anrede=ITeilnehmer.get('anrede').source.getTermByToken(
                         item.anrede).title,
                     unternehmen='<br>'.join(rcu),
                     vorname=item.vorname,
                     status=lfs.getTerm(kursteilnehmer.status).title,
                     journal=je,
                     bestanden=results['comment'])
            yield d

    def gVt(self, value):
        if value:
            return ITeilnehmer.get('titel').source.getTermByToken(value).title

    def gVa(self, value):
        if value:
            return ITeilnehmer.get('anrede').source.getTermByToken(value).title

    def gLS(self, value):
        if value:
            return IKursteilnehmer.get('status').source(None).getTermByToken(value).title

    def namespace(self):
        tn = None
        unternehmenl = [] 
        ktns = []
        root = grok.getSite()
        if self.results:
            tn = self.results
            locate(root, tn, DefaultModel)
            for unternehmen in tn.unternehmen:
                locate(root, unternehmen, DefaultModel)
                unternehmenl.append(unternehmen)
            for ktn in tn.kursteilnehmer:
                locate(root, ktn, DefaultModel)
                ktns.append(ktn)
        return {'teilnehmer': tn, 'unternehmen': unternehmenl, 'kursteilnehmer': ktns}

    @action(u'Suchen')
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = Session()
        #sql = session.query(Teilnehmer).options(
        #    joinedload(Kursteilnehmer.antworten))
        #sql = sql.filter(Kursteilnehmer.teilnehmer_id == Teilnehmer.id)
        print data
        sql = session.query(Teilnehmer)
        if data.get('id') != "":
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.one()
