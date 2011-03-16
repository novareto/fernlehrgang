# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 


import grok

from megrok import resource
from hurry.jquery import jquery
from zope.interface import Interface
from uvc.layout.interfaces import IHeaders


class FernlehrgangResources(resource.ResourceLibrary):
    resource.name('flgresource')
    resource.path('static')
    resource.resource('jquery.tools.min.js')
    resource.resource('jquery.tablesorter.min.js')
    #resource.resource('jquery.tablesorter.pager.js')
    #resource.resource('jquery.metadata.js')
    resource.resource('jquery.autocomplete.js')
    resource.resource('flg.js')
    resource.resource('dropdown.js')
    resource.resource('flg.css')
    resource.resource('dynselect.js', depends=[jquery,])


class FernlehrgangResourceViewlet(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def render(self):
        jquery.need()
        FernlehrgangResources.need()
        return u''
        #return u'<script src="http://cdn.jquerytools.org/1.1.2/jquery.tools.min.js"></script>'

