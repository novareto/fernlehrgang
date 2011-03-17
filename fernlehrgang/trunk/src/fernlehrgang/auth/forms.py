# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok


from dolmen.forms.base import apply_data_event
from handler import Account, UserFolder
from interfaces import IAddUserForm
from megrok import navigation
from megrok.layout import Page
from uvc.layout.interfaces import IGlobalMenu
from uvc.layout.zeamform import Form
from zeam.form.base import Fields, action
from zope import interface, component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin

grok.templatedir('templates')


class BenuzterVerwaltung(grok.View):
    grok.title('Benutzerverwaltung')
    grok.context(interface.Interface)
    grok.require('zope.ManageApplication')
    navigation.sitemenuitem(IGlobalMenu, order=200)

    def render(self):
        self.redirect(self.application_url() + '/benutzer')


class UserList(Page):
    grok.name('index')
    grok.context(UserFolder)
    grok.require('uf.ueberfallmanager')
    
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
        users.addUser(data['login'],data['password'],data['real_name'],data['role'],data['zuordnung'])
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
        self.redirect(self.url(grok.getSite(), '/benutzer'))

    @action(u'Entfernen')
    def handle_add(self):
        del self.context.__parent__[self.context.__name__]
        self.redirect(self.url(grok.getSite(), '/benutzer'))