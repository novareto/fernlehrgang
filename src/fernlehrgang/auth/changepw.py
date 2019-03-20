# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import grok

from zope.component import getUtility
from fernlehrgang.lib.emailer import send_mail
from z3c.saconfig import Session
from fernlehrgang import models
from fernlehrgang.interfaces.app import IFernlehrgangApp


TEXT = u"""
Sehr geehrte Damen und Herren,

bitte öffnen Sie nachfolgenden Link um Ihr Passwort zurückzusetzen und ein neues Passwort zu vergeben.

https://online-fernlehrgang-weblogin.bghw.de/resetpassword?form.field.username=%s&form.field.challenge=%s

Sie haben kein neues Passwort angefordert? In diesem Fall ignorieren Sie diese Email.

Mit freundlichen Grüßen
Ihre Fernlehrgangsbetreuung
"""


TEXT_CONFIRM = u"""
Sehr geehrte Damen und Herren,

kürzlich wurde das Passwort für Ihren Zugang zum Fernlehrgang geändert.
Benutzername: %s

Wenn Sie diese Passwortänderung nicht angefordert haben, wenden Sie sich bitte an das Fernlehrgang-Team.


Web: http://www.bghw.de
E-Mail: fernlehrgang@bghw.de

Ihre Fernlehrgangsbetreuung

"""

def getUser(teilnehmer_id):
    session = Session()
    return session.query(models.Teilnehmer).get(int(teilnehmer_id))



class PasswordActions(grok.JSON):
    grok.context(IFernlehrgangApp)

    def get_user(self):
        mnr = self.request.form.get('username', None)
        if mnr and mnr.isdigit():
            user = getUser(mnr)
            if user:
                return dict(mnr=str(user.id), passwort=user.passwort, email=user.email)
        return {'auth': 0}

    def send_mail(self):
        user = self.request.form.get('username')
        mail = self.request.form.get('email')
        hash = self.request.form.get('hash_value')
        text = TEXT % (user, hash)
        send_mail('fernlehrgang@bghw.de', (mail, ), u"Fernlehrgang Passwortänderung", text)
        return {'success': 'true'}

    def set_user(self):
        username = self.request.form.get('username')
        password = self.request.form.get('password')
        if username and password:
            user = getUser(username)
            user.passwort = password
            return {'success': 'true'}
        return {'success': 'false'}

    def send_confirm(self):
        user = self.request.form.get('username')
        mail = self.request.form.get('email')
        text = TEXT_CONFIRM % (user)
        userobject = getUser(user)
        send_mail('fernlehrgang@bghw.de', (userobject.email, ), u"Fernlehrgang Passwortänderung", text)
        return {'success': 'true'}

