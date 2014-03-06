# -*- coding: utf-8 -*-

import uvclight
from cromlech.sqlalchemy import get_session
from fernlehrgang.models import Kursteilnehmer, ICalculateResults
from zope.interface import implementer
from .interfaces import IMembership
from uvclight.auth import Principal


class Membership(uvclight.Adapter):
    uvclight.context(Principal)
    uvclight.provides(IMembership)

    @property
    def courses(self):
        userid = int(self.context.id)
        session = get_session('fernlehrgang')
        ktns = session.query(Kursteilnehmer).filter(
                Kursteilnehmer.teilnehmer_id == userid).all()
        return [ktn.fernlehrgang for ktn in ktns]

    def get_course_result(self, courseid):
        userid = int(self.context.id)
        session = get_session('fernlehrgang')
        ktns = session.query(Kursteilnehmer).filter(
            Kursteilnehmer.teilnehmer_id == userid
            ).filter(Kursteilnehmer.fernlehrgang_id == courseid)

        if ktns.count() == 1:
            ktn = ktns.one()
            return ICalculateResults(ktn)
        return None

    def get_course_member(self, courseid):
        userid = int(self.context.id)
        session = get_session('fernlehrgang')
        ktn = session.query(Kursteilnehmer).filter(
            Kursteilnehmer.teilnehmer_id == userid
            ).filter(Kursteilnehmer.fernlehrgang_id == courseid)
        if ktn.count() == 1:
            ktn = ktn.one()
            return ktn
        return None
