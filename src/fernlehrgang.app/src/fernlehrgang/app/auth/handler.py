# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from fernlehrgang.models.user import User
from zope import component, interface, schema
from zope.password.interfaces import IPasswordManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.pluggableauth.interfaces import IPrincipalInfo, IAuthenticatorPlugin
from zope.location import LocationProxy, locate
from dolmen.authentication import UserLoginEvent
from zope.securitypolicy.principalrole import principalRoleManager


class PrincipalInfo(object):
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None


class UserAuthenticatorPlugin(object):
    grok.implements(IAuthenticatorPlugin)

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        account = self.get(credentials['login'])
        if account is None:
            return None
        if not account.checkPassword(credentials['password']):
            return None

        roles = principalRoleManager.getRolesForPrincipal(account.login)
        if account.role not in roles:
            principalRoleManager.assignRoleToPrincipal(
                account.role, account.login)
        
        return PrincipalInfo(id=account.login,
                             title=account.real_name,
                             description=account.real_name)

    def principalInfo(self, id):
        account = self.get(id)
        if account is None:
            return None
        return PrincipalInfo(id=account.login,
                             title=account.real_name,
                             description=account.real_name)

    def __iter__(self):
        session = Session()
        return iter(session.query(User).all())

    def __contains__(self, login):
        try:
            session = Session()
            c = session.query(User).filter(User.login == login).count()
            return bool(c > 0)
        except ValueError:
            return False

    def get(self, login):
        try:
            session = Session()
            query = session.query(User).filter(User.login == login)
            assert query.count() == 1
            user = LocationProxy(query.one())
            locate(user, self, str(login))
            return user
        except AssertionError, ValueError:
            pass
        return None

    def add(self, username, email, password, real_name, role):
        if not account in self:
            session = Session()
            user = User(
                login=username, email=email, password=password,
                real_name=real_name, role=role)
            session.add(user)

    def delete(self, user):
        session = Session()
        session.delete(user)


Benutzer = UserAuthenticatorPlugin()
grok.global_utility(Benutzer, name=u'Benutzer', direct=True)
