# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


from cromlech.sqlalchemy import get_session
from fernlehrgang.models.user import User
from zope.location import LocationProxy, locate


class Users(object):

    def __iter__(self):
        session = get_session('fernlehrgang')
        return iter(session.query(User).all())

    def __contains__(self, login):
        try:
            session = get_session('fernlehrgang')
            c = session.query(User).filter(User.login == login).count()
            return bool(c > 0)
        except ValueError:
            return False

    def get(self, login, default=None):
        try:
            session = get_session('fernlehrgang')
            query = session.query(User).filter(User.login == login)
            assert query.count() == 1
            user = LocationProxy(query.one())
            locate(user, self, str(login))
            return user
        except AssertionError, ValueError:
            pass
        return None

    def add(self, username, email, password, real_name, role):
        if not username in self:
            session = get_session('fernlehrgang')
            user = User(
                login=username, email=email, password=password,
                real_name=real_name, role=role)
            session.add(user)

    def delete(self, user):
        session = get_session('fernlehrgang')
        session.delete(user)


Benutzer = Users()
