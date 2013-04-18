# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok


from dolmen.forms.base import apply_data_event
from handler import Account, UserFolder
from interfaces import IAddUserForm
from megrok.layout import Page
from uvc.layout import MenuItem
from uvc.layout.interfaces import IFooter
from uvc.layout.forms.components import Form
from zeam.form.base import Fields, action
from zope import interface, component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from dolmen.menu import menuentry
from zope.securitypolicy.interfaces import IPrincipalRoleManager

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
    grok.context(UserFolder)
    grok.require('zope.ManageApplication')
    
    def update(self):
        users = component.getUtility(IAuthenticatorPlugin, 'principals')
        self.users = users.listUsers()
   

class AddUser(Form): 
    grok.context(UserFolder)
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
        users.addUser(data['login'], data['email'], data['password'], data['real_name'], data['role'])
        self.redirect(self.url(grok.getSite(), '/benutzer'))


class EditUser(Form): 
    grok.name('edit')
    grok.context(Account)
    grok.require('zope.ManageApplication')
    label = u"Benutzer bearbeiten"

    fields = Fields(IAddUserForm)
    ignoreContent = False

    @action(u'Bearbeiten')
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Es ist ein Fehler aufgetreten', 'warning')
            return
        changes = apply_data_event(self.fields, self.context, data)
        role_manager = IPrincipalRoleManager(grok.getSite())
        for role_id, setting in role_manager.getRolesForPrincipal(data['login']):
            role_manager.removeRoleFromPrincipal(role_id, data['login'])
        role_manager.assignRoleToPrincipal(data['role'], data['login'])
        print role_manager.getRolesForPrincipal(data['login'])
        self.redirect(self.url(grok.getSite(), '/benutzer'))

    @action(u'Entfernen')
    def handle_delete(self):
        data, errors = self.extractData()
        del self.context.__parent__[self.context.__name__]
        role_manager = IPrincipalRoleManager(grok.getSite())
        for role_id, setting in role_manager.getRolesForPrincipal(data['login']):
            role_manager.removeRoleFromPrincipal(role_id, data['login'])
        self.redirect(self.url(grok.getSite(), '/benutzer'))
