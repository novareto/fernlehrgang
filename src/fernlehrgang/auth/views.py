import grok

from fernlehrgang.models import Account
from fernlehrgang.browser import Page, Form
from zeam.form.base import Fields, action
from zope import component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from grokcore.chameleon.components import ChameleonPageTemplateFile
from .interfaces import IAddUserForm
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.browser.utils import apply_data_event


grok.templatedir("templates")


class UserList(Page):
    grok.name("users")
    grok.context(IFernlehrgangApp)
    grok.require("zope.Public")

    def update(self):
        users = component.getUtility(IAuthenticatorPlugin, "principals")
        self.users = users.listUsers()


class AddUser(Form):
    grok.context(IFernlehrgangApp)
    grok.require("zope.Public")
    label = "Benutzer anlegen"

    fields = Fields(IAddUserForm)

    @action("Anlegen")
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash("Es ist ein Fehler aufgetreten", "warning")
            return
        users = component.getUtility(IAuthenticatorPlugin, "principals")
        users.addUser(
            data["login"],
            data["email"],
            data["password"],
            data["real_name"],
            data["role"],
        )
        self.flash("Der Benutzer wurde angelegt.")
        self.redirect(self.url(grok.getSite(), "users"))


class EditUser(Form):
    grok.name("edit")
    grok.context(Account)
    # grok.require("zope.ManageApplication")
    label = "Benutzer bearbeiten"

    fields = Fields(IAddUserForm)
    ignoreContent = False

    def updateForm(self):
        super(EditUser, self).updateForm()
        pw = self.fieldWidgets.get("form.field.password")
        confirm = self.fieldWidgets.get("form.field.confirm_password")
        pw.template = ChameleonPageTemplateFile("templates/password.cpt")
        confirm.template = ChameleonPageTemplateFile("templates/password.cpt")

    @action("Bearbeiten")
    def handle_add(self):
        data, errors = self.extractData()
        if errors:
            self.flash("Es ist ein Fehler aufgetreten", "warning")
            return
        apply_data_event(self.fields, self.context, data)
        self.redirect(self.url(grok.getSite(), "/users"))

    @action("Entfernen")
    def handle_delete(self):
        data, errors = self.extractData()
        from z3c.saconfig import Session

        session = Session()
        session.delete(self.context)
        self.flash("Der Benutzer wurde gelöscht")
        self.redirect(self.url(grok.getSite(), "/users"))
