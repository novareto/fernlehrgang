# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import uvclight
from zope import component
from sqlalchemy import func, and_
from fernlehrgang import models


from fernlehrgang.models import IFernlehrgang
from fernlehrgang.models.kursteilnehmer import lieferstopps
from fernlehrgang.app.browser.viewlets import NavigationMenu
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from cromlech.sqlalchemy import get_session
from pygooglechart import PieChart2D, PieChart3D



@uvclight.menuentry(NavigationMenu, order=300)
class FernlehrgangStatistik(uvclight.Page):
    uvclight.context(IFernlehrgang)
    uvclight.title(u"Statistik")

    template = uvclight.get_template('fernlehrgangstatistik.cpt', __file__)

    title = u"Statistik Fernlehrgang"
    alle_kursteilnehmer = 0
    kursteilnehmer_detail = []

    @property
    def description(self):
        return u"Hier Sie verschiedene Statstiken zum Fernlehrgang '%s' aufrufen" % self.context.titel

    @property
    def isNotReader(self):
        ret = True
        # BBB
        return ret

    def update(self):
        session = get_session('fernlehrgang') 
        lfs = lieferstopps(None)
        self.alle_kursteilnehmer = len(self.context.kursteilnehmer)
        sql = session.query(models.Kursteilnehmer)
        kursteilnehmer_status = session.query(models.Kursteilnehmer.status, func.count()).filter(
            models.Kursteilnehmer.fernlehrgang_id == self.context.id).group_by(
            models.Kursteilnehmer.status).all()
        self.kursteilnehmer_detail = [(lfs.getTermByToken(x[0]).title, x[1]) for x in kursteilnehmer_status]     

    def getAntworten(self):
        session = get_session('fernlehrgang') 
        return session.query(models.Lehrheft.nummer, func.count()).filter(
            and_(models.Kursteilnehmer.fernlehrgang_id==self.context.id,
                 models.Lehrheft.fernlehrgang_id == self.context.id,
                 models.Kursteilnehmer.id==models.Antwort.kursteilnehmer_id,
                 models.Antwort.lehrheft_id == models.Lehrheft.id)).group_by(
                 models.Lehrheft.nummer).order_by(
                 models.Lehrheft.nummer).all()
        
