# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from fanstatic import Library, Resource
from zope.interface import Interface
from uvc.layout.interfaces import IHeaders

from uvc.widgets import double, DatePickerCSS


library = Library('fernlehrgang', 'static')

ts = Resource(library, 'jquery.tablesorter.min.js')
css = Resource(library, 'flg.css', depends=[DatePickerCSS])
js = Resource(library, 'flg.js', depends=[double,])


class FernlehrgangResourceViewlet(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def render(self):
        ts.need()
        css.need()
        js.need()
        return u''
