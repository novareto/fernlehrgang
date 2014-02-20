# package

import grok
from uvc.layout.forms.components import AddForm, Form
from zope.publisher.interfaces.http import IHTTPRequest
from zope.i18n.interfaces import IUserPreferredLanguages


class Form(Form):
    grok.require('dolmen.content.Add')
    grok.baseclass()


class AddForm(AddForm):
    grok.require('dolmen.content.Add')
    grok.baseclass()


class GermanBrowserLangugage(grok.Adapter):                                     
    grok.context(IHTTPRequest)
    grok.implements(IUserPreferredLanguages)

    def getPreferredLanguages(self):
        return ['de', 'de-de']
