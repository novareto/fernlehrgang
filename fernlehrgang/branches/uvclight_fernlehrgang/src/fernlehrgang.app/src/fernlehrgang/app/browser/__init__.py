# package

import uvclight

from uvclight import Form, AddForm, EditForm, DeleteForm, DefaultView
from grokcore.component import Adapter
from zope.publisher.interfaces.http import IHTTPRequest
from zope.i18n.interfaces import IUserPreferredLanguages


class GermanBrowserLangugage(Adapter):
    uvclight.context(IHTTPRequest)
    uvclight.implements(IUserPreferredLanguages)

    def getPreferredLanguages(self):
        return ['de', 'de-de']


def pagetemplate(path):
    return uvclight.get_template(path, __file__)
