# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


from cromlech.sqlalchemy import get_session
from fernlehrgang.models.teilnehmer import Teilnehmer
from zope.location import LocationProxy, locate


class Users(object):

    def __iter__(self):
        session = get_session('fernlehrgang')
        return iter(session.query(Teilnehmer).all())

    def __contains__(self, login):
        try:
            session = get_session('fernlehrgang')
            c = session.query(Teilnehmer).filter(Teilnehmer.id == login).count()
            return bool(c > 0)
        except ValueError:
            return False

    def get(self, login, default=None):
        try:
            session = get_session('fernlehrgang')
            query = session.query(Teilnehmer).filter(Teilnehmer.id == login)
            assert query.count() == 1
            user = LocationProxy(query.one())
            locate(user, self, str(login))
            return user
        except AssertionError, ValueError:
            pass
        return None


Benutzer = Users()
