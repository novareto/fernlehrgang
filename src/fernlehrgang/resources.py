# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


import grok

from fanstatic import Library, Resource
from zope.interface import Interface
from uvc.layout.interfaces import IHeaders
from js.bootstrap import bootstrap_js
from uvc.widgets import double, DatePickerCSS
from js.jquery import jquery
from uvc.tbskin.resources import TBSkinViewlet


library = Library('fernlehrgang', 'static')

css = Resource(library, 'flg.css', depends=[DatePickerCSS])
responsive = Resource(library, 'responsive.css')
tabs = Resource(library, 'tabs.js', depends=[responsive, bootstrap_js, jquery])
js = Resource(library, 'flg.js', depends=[tabs, double, ])
register_js = Resource(library, 'register.js', depends=[jquery])


class FernlehrgangResourceViewlet(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def update(self):
        css.need()
        js.need()

    def render(self):
        return u''


class MyTBSkinViewlet(TBSkinViewlet):
    pass
