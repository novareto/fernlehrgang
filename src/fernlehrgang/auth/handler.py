# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from z3c.saconfig import Session
from fernlehrgang.models import Account
from zope import component, interface, schema
from zope.password.interfaces import IPasswordManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.pluggableauth.interfaces import IPrincipalInfo, IAuthenticatorPlugin
from zope.pluggableauth.factories import Principal


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
    grok.name("principals")

    @property
    def session(self):
        return Session()

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ("login" in credentials and "password" in credentials):
            return None
        account = self.getAccount(credentials["login"])
        if account is None:
            return None
        if not account.checkPassword(credentials["password"]):
            return None
        return PrincipalInfo(
            id=account.login, title=account.real_name, description=account.role
        )

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is None:
            return None
        return PrincipalInfo(
            id=account.login, title=account.real_name, description=account.role
        )

    def getAccount(self, login):
        return self.session.query(Account).get(login)

    def addUser(self, username, email, password, real_name, role):
        if username not in self.user_folder:
            user = Account(username, email, password, real_name, role)
            self.session.add(user)
            # role_manager = IPrincipalRoleManager(grok.getSite())
            # role_manager.assignRoleToPrincipal(role, username)

    def listUsers(self):
        return self.sessions.query(Account).all()


from zope.interface import Interface
from dolmen.security.policies import ExtraRolePermissionMap
from zope.securitypolicy.interfaces import Allow, Deny
from zope.securitypolicy.securitymap import SecurityMap
from dolmen.security.policies.principalrole import ExtraRoleMap


class HomepageRolePermissionManager(ExtraRoleMap):
    grok.context(Interface)

    def _compute_extra_data(self):
        extra_map = SecurityMap()
        import pdb; pdb.set_trace()
        extra_map.addCell('zope.ManageContent', 'test.role', Deny)
        return extra_map
