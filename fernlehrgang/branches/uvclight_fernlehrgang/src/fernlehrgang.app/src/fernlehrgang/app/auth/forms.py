# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from dolmen.forms.base import apply_data_event
from uvclight import Page, MenuItem, Form
from uvclight.interfaces import IGlobalMenu
from dolmen.forms.base import Fields, action
from zope import interface

from .interfaces import IAddUserForm
from .handler import USERS
from fernlehrgang.models.user import User
from fernlehrgang.app.interfaces import IFernlehrgangApp


from uvclight.auth import Login


class Login(Login):
    title = message = u"Bitte melden Sie sich an."
    template = uvclight.get_template('login_form.cpt', __file__)


class BenutzerMI(MenuItem):
    uvclight.context(interface.Interface)
    #uvclight.require('uvc.managefernlehrgang')
    uvclight.title(u'Benutzerverwaltung')
    uvclight.menu(IGlobalMenu)

    @property
    def action(self):
        return self.view.application_url() + '/benutzer'


class UserList(Page):
    uvclight.name('benutzer_listing')
    uvclight.context(IFernlehrgangApp)
    uvclight.require('uvc.managefernlehrgang')

    template = uvclight.get_template("userlist.cpt", __file__)

    def update(self):
        self.users = list(USERS)


class AddUser(Form):
    uvclight.context(IFernlehrgangApp)
    uvclight.require('uvc.managefernlehrgang')
    label = u"Benutzer anlegen"

    fields = Fields(IAddUserForm)

    @action(u'Anlegen')
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Es ist ein Fehler aufgetreten', 'warning')
            return
        users = USERS
        users.add(data['login'], data['email'],
                  data['password'], data['real_name'], data['role'])
        self.redirect(self.url(uvclight.getSite()) + '/benutzer_listing')


class EditUser(Form):
    uvclight.name('edit')
    uvclight.context(User)
    uvclight.require('uvc.managefernlehrgang')
    label = u"Benutzer bearbeiten"

    fields = Fields(IAddUserForm).omit('confirm_password')
    ignoreContent = False

    def updateForm(self):
        super(EditUser, self).updateForm()
        pw = self.fieldWidgets.get('form.field.password')
        pw.template = uvclight.get_template('password.cpt', __file__)

    @action(u'Bearbeiten')
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Es ist ein Fehler aufgetreten', 'warning')
            return
        apply_data_event(self.fields, self.context, data)
        self.redirect(self.url(uvclight.getSite()) + '/benutzer_listing')

    @action(u'Entfernen')
    def handle_delete(self):
        data, errors = self.extractData()
        self.context.__parent__.delete(self.context)
        self.redirect(self.url(uvclight.getSite()) + '/benutzer_listing')
