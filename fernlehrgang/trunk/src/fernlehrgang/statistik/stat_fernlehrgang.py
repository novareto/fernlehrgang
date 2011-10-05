# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c import saconfig
from zope import component
from dolmen import menu
from megrok import layout
from sqlalchemy import func, and_
from fernlehrgang import models


from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import lieferstopps
from fernlehrgang.viewlets import NavigationMenu
from zope.schema.interfaces import IVocabularyFactory


from pygooglechart import PieChart2D, PieChart3D

grok.templatedir('templates')


@menu.menuentry(NavigationMenu, order=300)
class FernlehrgangStatistik(layout.Page):
    grok.context(IFernlehrgang)
    grok.title(u"Statstik Fernlehrgang")

    title = u"Statistik Fernlehrgang"
    alle_kursteilnehmer = 0
    kursteilnehmer_detail = []

    @property
    def description(self):
        return u"Hier Sie verschiedene Statstiken zum Fernlehrgang '%s' aufrufen" % self.context.titel

    def update(self):
        session = saconfig.Session()
        lfs = lieferstopps(None)
        self.alle_kursteilnehmer = len(self.context.kursteilnehmer)
        sql = session.query(models.Kursteilnehmer)
        kursteilnehmer_status = session.query(models.Kursteilnehmer.status, func.count()).filter(
            models.Kursteilnehmer.fernlehrgang_id == self.context.id).group_by(
            models.Kursteilnehmer.status).all()
        self.kursteilnehmer_detail = [(lfs.getTermByToken(x[0]).title, x[1]) for x in kursteilnehmer_status]     

    def getAntworten(self):
        session = saconfig.Session()
        return session.query(models.Lehrheft.nummer, func.count()).filter(
            and_(models.Kursteilnehmer.fernlehrgang_id==self.context.id,
                 models.Kursteilnehmer.id==models.Antwort.kursteilnehmer_id,
                 models.Antwort.lehrheft_id == models.Lehrheft.id)).group_by(
                 models.Lehrheft.nummer).order_by(
                 models.Lehrheft.nummer).all()
        
