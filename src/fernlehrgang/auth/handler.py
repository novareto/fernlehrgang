# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope import component, interface, schema
from zope.password.interfaces import IPasswordManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.pluggableauth.interfaces import IPrincipalInfo, IAuthenticatorPlugin



class PrincipalInfo(object):
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None


class UserAuthenticatorPlugin(grok.LocalUtility):
    grok.implements(IAuthenticatorPlugin)
    grok.name('principals')

    def __init__(self):
        self.user_folder = UserFolder()
        
    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        account = self.getAccount(credentials['login'])
        if account is None:
            return None
        if not account.checkPassword(credentials['password']):
            return None
        return PrincipalInfo(id=account.login,
                             title=account.real_name,
                             description=account.real_name)

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is None:
            return None
        return PrincipalInfo(id=account.login,
                             title=account.real_name,
                             description=account.real_name)

    def getAccount(self, login):
        return login in self.user_folder and self.user_folder[login] or None
    
    def addUser(self, username, email, password, real_name, role):
        if username not in self.user_folder:
            user = Account(username, email, password, real_name, role)
            self.user_folder[username] = user
            role_manager = IPrincipalRoleManager(grok.getSite())
            role_manager.assignRoleToPrincipal(role, username)
            
    def listUsers(self):
        return self.user_folder.values()


class UserFolder(grok.Container):
    pass


class Account(grok.Model):
    def __init__(self, name, email, password, real_name, role):
        self.login = name
        self.email = email
        self.real_name = real_name
        self.role = role
        self.password = password

    def checkPassword(self, password):
        if password == self.password:
            return True
        return False

    def getEmail(self):
        if hasattr(self, 'email'):
            return self.email
        return ''
