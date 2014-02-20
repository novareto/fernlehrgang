# package

import grok

from uvclight import Form
from zope.publisher.interfaces.http import IHTTPRequest
from zope.i18n.interfaces import IUserPreferredLanguages
from dolmen.forms.crud import Add as AddForm, Display as DefaultView, Edit


class Form(Form):
    grok.require('dolmen.content.Add')
    grok.baseclass()


class GermanBrowserLangugage(grok.Adapter):                                     
    grok.context(IHTTPRequest)
    grok.implements(IUserPreferredLanguages)

    def getPreferredLanguages(self):
        return ['de', 'de-de']
