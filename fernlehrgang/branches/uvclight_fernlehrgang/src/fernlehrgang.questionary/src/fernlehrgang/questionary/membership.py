# -*- coding: utf-8 -*-

import grok
from zope.interface import implementer
from z3c.saconfig import Session
from fernlehrgang.models import Kursteilnehmer, ICalculateResults
from .interfaces import IMembership, IMember


class Membership(grok.Adapter):
    grok.context(IMember)
    grok.provides(IMembership)

    @property
    def courses(self):
        userid = int(self.context.id)
        session = Session()
        ktns = session.query(Kursteilnehmer).filter(
                Kursteilnehmer.teilnehmer_id == userid).all()
        return [ktn.fernlehrgang for ktn in ktns]

    def get_course_result(self, courseid):
        userid = int(self.context.id)
        session = Session()
        ktns = session.query(Kursteilnehmer).filter(
            Kursteilnehmer.teilnehmer_id == userid
            ).filter(Kursteilnehmer.fernlehrgang_id == courseid)
        
        if ktns.count() == 1:
            ktn = ktns.one()
            return ICalculateResults(ktn)
        return None

    def get_course_member(self, courseid):
        userid = int(self.context.id)
        session = Session()
        ktn = session.query(Kursteilnehmer).filter(
            Kursteilnehmer.teilnehmer_id == userid
            ).filter(Kursteilnehmer.fernlehrgang_id == courseid)
        if ktn.count() == 1:
            ktn = ktn.one()
            return ktn
        return None

