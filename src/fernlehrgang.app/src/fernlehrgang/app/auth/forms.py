# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from dolmen.forms.base import apply_data_event
from dolmen.menu import menuentry
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.layout import Page
from uvc.layout import MenuItem
from uvc.layout.forms.components import Form
from uvc.layout.interfaces import IFooter
from zeam.form.base import Fields, action
from zope import interface, component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from .interfaces import IAddUserForm
from .handler import UserAuthenticatorPlugin
from fernlehrgang.models.user import User


grok.templatedir('templates')


class BenutzerMI(MenuItem):
    grok.context(interface.Interface)
    grok.require('zope.ManageApplication')
    grok.title(u'Benutzerverwaltung')
    grok.viewletmanager(IFooter)

    @property
    def action(self):
        return self.view.application_url() + '/benutzer'


class UserList(Page):
    grok.name('index')
    grok.context(UserAuthenticatorPlugin)
    grok.require('zope.ManageApplication')
    
    def update(self):
        self.users = list(self.context)
   

class AddUser(Form): 
    grok.context(UserAuthenticatorPlugin)
    grok.require('zope.ManageApplication')
    label = u"Benutzer anlegen"

    fields = Fields(IAddUserForm)

    @action(u'Anlegen')
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Es ist ein Fehler aufgetreten', 'warning')
            return
        users = component.getUtility(IAuthenticatorPlugin, 'principals')
        users.add(data['login'], data['email'],
                  data['password'], data['real_name'], data['role'])
        self.redirect(self.url(grok.getSite(), '/benutzer'))


class EditUser(Form): 
    grok.name('edit')
    grok.context(User)
    grok.require('zope.ManageApplication')
    label = u"Benutzer bearbeiten"

    fields = Fields(IAddUserForm)
    ignoreContent = False

    def updateForm(self):                                                       
        super(EditUser, self).updateForm()                                
        pw = self.fieldWidgets.get('form.field.password')                       
        confirm = self.fieldWidgets.get('form.field.confirm_password')
        pw.template = ChameleonPageTemplateFile('templates/password.cpt')
        confirm.template = ChameleonPageTemplateFile('templates/password.cpt') 

    @action(u'Bearbeiten')
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Es ist ein Fehler aufgetreten', 'warning')
            return
        changes = apply_data_event(self.fields, self.context, data)
        self.redirect(self.url(grok.getSite(), '/benutzer'))

    @action(u'Entfernen')
    def handle_delete(self):
        data, errors = self.extractData()
        self.context.__parent__.delete(self.context)
        self.redirect(self.url(grok.getSite(), '/benutzer'))
