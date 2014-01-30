# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from dolmen.uploader.resources.hayageek import uploader as hayageek
from fanstatic import Library, Resource
from js.bootstrap_wysihtml5 import bootstrap_wysihtml5
from js.jquery import jquery
from uvc.layout.interfaces import IHeaders
from uvc.widgets import double, DatePickerCSS
from zope.interface import Interface


library = Library('fernlehrgang.app.browser', 'static')
css = Resource(library, 'flg.css', depends=[DatePickerCSS])
js = Resource(library, 'flg.js', depends=[double, bootstrap_wysihtml5])
register_js = Resource(library, 'register.js', depends=[jquery])
upload = Resource(library, 'upload.js', depends=[hayageek], bottom=True)


class FernlehrgangResourceViewlet(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def render(self):
        css.need()
        js.need()
        return u''
