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
from fernlehrgang.interfaces.journal import IJournalEntry
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

    ignoreRequest = False
    postOnly = False
    results = None 

    def update(self):
        chosen_js.need()
        chosen_css.need()
        chosen_ajax.need()

    def updateWidgets(self):
        super(TeilnehmerSuche, self).updateWidgets()
        field_id = self.fieldWidgets.get('form.field.id')
        field_id.template = ChameleonPageTemplateFile('templates/select.cpt')

    def gVt(self, value):
        if value:
            return ITeilnehmer.get('titel').source.getTermByToken(value).title

    def gVa(self, value):
        if value:
            return ITeilnehmer.get('anrede').source.getTermByToken(value).title

    def gLS(self, value):
        if value:
            return IKursteilnehmer.get('status').source(None).getTermByToken(value).title

    def gKV(self, value):
        if value:
            return ITeilnehmer.get('kategorie').source.by_value.get(str(value)).title

    def gU(self, value):
        if value:
            return IKursteilnehmer.get('un_klasse').source(None).getTermByToken(value).title

    def gBR(self, value):
        if value:
            return IKursteilnehmer.get('branche').source(None).getTermByToken(value).title

    def getStatus(self, value):
        if value:
            try:
                return IJournalEntry.get('status').source(None).getTerm(value).title
            except:
                return u"--> %s" % value

    def getSession(self):
        key = "fernlehrgang.teilnehmer"
        from zope.session.interfaces import ISession
        session = ISession(self.request)[key]
        return session

    def namespace(self):
        tn = None
        unternehmenl = [] 
        ktns = []
        root = grok.getSite()
        zs = self.getSession()
        if zs.get('tn'):
            tn = zs.get('tn')
            session = Session()
            tn = session.query(Teilnehmer).get(int(tn))
            for unternehmen in tn.unternehmen:
                unternehmenl.append(unternehmen)
            for ktn in tn.kursteilnehmer:
                ktns.append(ktn)
        return {'teilnehmer': tn, 'unternehmen': unternehmenl, 'kursteilnehmer': ktns}

    @action(u'Suchen')
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        if errors:
            return
        session = Session()
        sql = session.query(Teilnehmer)
        if data.get('id') != "":
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        zs = self.getSession()
        zs['tn'] = data.get('id') 
