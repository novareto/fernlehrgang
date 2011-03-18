# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from megrok import resource
from hurry.jquery import jquery
from hurry.jquerytools import jquerytools
from zope.interface import Interface
from uvc.layout.interfaces import IHeaders

from uvc.widgets import double, DatePickerCSS


class FernlehrgangResources(resource.ResourceLibrary):
    resource.name('flgresource')
    resource.path('static')
    resource.resource('jquery.tablesorter.min.js')
    resource.resource('flg.css', depends=[DatePickerCSS])
    resource.resource('flg.js', depends=[double,])


class FernlehrgangResourceViewlet(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def render(self):
        jquerytools.need()
        FernlehrgangResources.need()
        return u''
