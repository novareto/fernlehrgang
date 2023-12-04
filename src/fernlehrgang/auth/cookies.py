# -*- coding: utf-8 -*-
"""This implementation is based on the ``wc.cookiecredentials`` package
from Philipp von Weitershausen.
"""

import base64
import urllib
import grokcore.component as grok
from zope.interface import Interface, implementer
from zope.schema import ASCIILine
from zope.pluggableauth.interfaces import ICredentialsPlugin
from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from zope.publisher.interfaces.http import IHTTPRequest
from zope.session.interfaces import ISession


class ICookieCredentials(Interface):
    """A Credentials Plugin based on cookies."""

    cookie_name = ASCIILine(
        title="Cookie name",
        description="Name of the cookie for storing credentials.",
        required=True,
    )


@implementer(ICredentialsPlugin, ICookieCredentials)
class CookiesCredentials(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.name("cookies")
    grok.provides(ICredentialsPlugin)

    # ILocation's information
    __parent__ = None

    # Required by zope.pluggableauth's IBrowserFormChallenger
    loginpagename = "login"
    loginfield = "login"
    passwordfield = "password"

    # Required by zope.pluggableauth's ICredentialsPlugin
    challengeProtocol = None
    cookie_name = "dolmen.authcookie"

    @staticmethod
    def make_cookie(login, password):
        credstr = f"{login.decode('utf-8')}:{password.decode('utf-8')}"
        val = base64.encodebytes(credstr.encode("utf-8"))
        return urllib.parse.quote(val)

    def extractCredentials(self, request):
        if not IHTTPRequest.providedBy(request):
            return

        login = request.get(self.loginfield, None)
        password = request.get(self.passwordfield, None)
        cookie = request.get(self.cookie_name, None)

        if login and password:
            login = login.encode("utf-8")
            password = password.encode("utf-8")
            cookie = self.make_cookie(login, password)
            request.response.setCookie(self.cookie_name, cookie, path="/")
        elif cookie:
            val = base64.decodebytes(urllib.parse.unquote(cookie).encode("utf-8"))
            login, password = val.split(b":")
        else:
            return

        return {"login": login.decode("utf-8"), "password": password.decode("utf-8")}

    def logout(self, request):
        if not IHTTPRequest.providedBy(request):
            return
        request.response.expireCookie(self.cookie_name, path="/")
        session = ISession(request, None)
        if session is not None:
            session.delete()
