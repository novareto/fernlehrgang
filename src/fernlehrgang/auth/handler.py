# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok


from fernlehrgang import models
from z3c.saconfig import Session
from zope.interface import implementer
from grokcore.content import IContainer
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.pluggableauth.interfaces import IPrincipalInfo, IAuthenticatorPlugin
from zope.location import ILocation, Location, LocationProxy, locate


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

    def __init__(self):
        self.user_folder = UserFolder()

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
            id=account.login, title=account.real_name, description=account.real_name
        )

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is None:
            return None
        return PrincipalInfo(
            id=account.login, title=account.real_name, description=account.real_name
        )

    def getAccount(self, login):
        return login in self.user_folder and self.user_folder[login] or None

    def addUser(self, username, email, password, real_name, role):
        if username not in self.user_folder:
            user = models.Account(
                username=username,
                login=username,
                email=email,
                password=password,
                real_name=real_name,
                role=role,
            )
            self.user_folder.add(user)
            role_manager = IPrincipalRoleManager(grok.getSite())
            role_manager.assignRoleToPrincipal(role, username)

    def listUsers(self):
        return self.user_folder.values()


@implementer(IContainer)
class UserFolder(Location):

    __name__ = "benutzer"

    @property
    def __parent__(self):
        return grok.getApplication()

    @property
    def session(self):
        return Session()

    def values(self):
        return self.session.query(models.Account)

    def get(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        model = self.session.query(models.Account).get(str(key))
        if not model:
            return None
        locate(model, self, model.login)
        return model

    def add(self, item):
        try:
            self.session.add(item)
        except Exception as e:
            # This might be a bit too generic
            return e

    def delete(self, item):
        self.session.delete(item)
