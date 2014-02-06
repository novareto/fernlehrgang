# -*- coding: utf-8 -*-

import grok

from dolmen.content import Container, nofactory
from fernlehrgang.app.auth.handler import PrincipalInfo
from fernlehrgang.models import Teilnehmer
from z3c.saconfig import Session
from zope.pluggableauth.interfaces import (
    AuthenticatedPrincipalCreated, IAuthenticatorPlugin,
    IFoundPrincipalFactory, IAuthenticatedPrincipalFactory)
from zope.interface import implementer
from zope.publisher.interfaces import IRequest
from .interfaces import IMember, IMemberInfo
from zope.pluggableauth.factories import Principal
from zope.event import notify


@implementer(IMemberInfo)
class MemberInfo(PrincipalInfo):
    """A fernlehrgang member abstraction.
    """
    model = None

    
@implementer(IMember)
class Member(Principal):
    """A fernlehrgang member.
    """
    def __init__(self, id, title, description, model):
        Principal.__init__(self, id, title, description)
        self.model = model
    

class MemberFactory(grok.MultiAdapter):
    grok.adapts(IMemberInfo, IRequest)
    grok.implements(IAuthenticatedPrincipalFactory)
    grok.provides(IAuthenticatedPrincipalFactory)

    def __init__(self, info, request):
        self.info = info
        self.request = request

    def __call__(self, authentication):
        principal = Member(authentication.prefix + self.info.id,
                           self.info.title,
                           self.info.description, self.info.model)
        notify(AuthenticatedPrincipalCreated(
            authentication, principal, self.info, self.request))
        return principal


class FoundMemberFactory(grok.Adapter):
    grok.context(IMemberInfo)
    grok.implements(IFoundPrincipalFactory)
    grok.provides(IFoundPrincipalFactory)

    def __call__(self, authentication):
        principal = Member(authentication.prefix + self.info.id,
                              self.info.title,
                              self.info.description, self.info.model)
        notify(AuthenticatedPrincipalCreated(
            authentication, principal, self.info, self.request))
        return principal


class RDBUsersAuthenticatorPlugin(grok.GlobalUtility):
    grok.implements(IAuthenticatorPlugin)
    grok.name('rdbauth')

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None

        userid = credentials.get('login')
        passwd = credentials.get('password')
        if userid is None or passwd is None:
            return None
        else:
            try:
                userid = int(userid)
            except ValueError:
                return None
        
        session = Session()
        if userid not in ["admin"]:
            results = session.query(Teilnehmer).filter(Teilnehmer.id==userid)
            if results.count() == 1:
                user = results.one()
                if user and user.passwort == passwd:
                    fullname = u"%s %s" % (user.name, user.vorname)
                    info = MemberInfo(
                        id=str(userid), title=fullname, description=fullname)
                    info.model = user
                    return info
        return None
            
    def principalInfo(self, id):
        try:
            id = int(id)
        except ValueError:
            return None

        session = Session()
        results = session.query(Teilnehmer).filter(Teilnehmer.id==id)

        if results.count() != 1:
            return None

        user = results.one()
        if user:
            fullname = u"%s %s" % (user.name, user.vorname)
            info = MemberInfo(id=str(id), title=fullname, description=fullname)
            info.model = user
            return info
