# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c import saconfig
from zope import component
from dolmen import menu
from grokcore import layout
from sqlalchemy import func, and_
from fernlehrgang import models
from uvc.layout import Page


from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import lieferstopps
from fernlehrgang.viewlets import NavigationMenu
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from zope.pluggableauth.interfaces import IAuthenticatorPlugin


grok.templatedir('templates')


@menu.menuentry(NavigationMenu, order=300)
class FernlehrgangStatistik(Page):
    grok.context(IFernlehrgang)
    grok.title(u"Statistik")

    title = u"Statistik Fernlehrgang"
    alle_kursteilnehmer = 0
    kursteilnehmer_detail = []

    @property
    def description(self):
        return u"Hier Sie verschiedene Statstiken zum Fernlehrgang '%s' aufrufen" % self.context.titel

    @property
    def isNotReader(self):
        ret = True
        account = getUtility(IAuthenticatorPlugin, "principals").getAccount(self.request.principal.id)
        if account:
            if "uvc.reader" == account.role:
                ret = False
        return ret

    def update(self):
        session = saconfig.Session()
        lfs = lieferstopps(None)
        self.alle_kursteilnehmer = session.query(func.count(models.Kursteilnehmer.id)).filter(models.Kursteilnehmer.fernlehrgang_id == self.context.id).one()[0] 
        sql = session.query(models.Kursteilnehmer)
        kursteilnehmer_status = session.query(models.Kursteilnehmer.status, func.count()).filter(
            models.Kursteilnehmer.fernlehrgang_id == self.context.id).group_by(
            models.Kursteilnehmer.status).all()
        self.kursteilnehmer_detail = [(lfs.getTermByToken(x[0]).title, x[1]) for x in kursteilnehmer_status]     
        print self.kursteilnehmer_detail

    def getAntworten(self):
        session = saconfig.Session()
        i = 0
        if self.context.typ == '5':
            for ktn in self.context.kursteilnehmer:
                if len(ktn.antworten) > 0:
                    i+=1
                if len(ktn.antworten) > 10:
                    print "FUCK OFF", ktn.teilnehmer_id
            return [[self.context.lehrhefte[0].nummer, i]]

        return session.query(models.Lehrheft.nummer, func.count()).filter(
            and_(models.Kursteilnehmer.fernlehrgang_id==self.context.id,
                 models.Lehrheft.fernlehrgang_id == self.context.id,
                 models.Kursteilnehmer.id==models.Antwort.kursteilnehmer_id,
                 models.Antwort.lehrheft_id == models.Lehrheft.id)).group_by(
                 models.Lehrheft.nummer).order_by(
                 models.Lehrheft.nummer).all()
       
    def chartUser(self):
        import pygal
        pie_chart = pygal.Pie()
        pie_chart.title = 'Benutzerverteilung nach Status'
        for x in self.kursteilnehmer_detail:
            pie_chart.add(x[0], x[1])
        return pie_chart.render()
