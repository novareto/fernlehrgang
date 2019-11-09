# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


import grok

from fanstatic import Library, Resource
from zope.interface import Interface
from fernlehrgang.slots.interfaces import IHeaders
from js.jquery import jquery


library = Library("fernlehrgang", "static")

chosen_js = Resource(library, "chosen.jquery.js", depends=[jquery])
chosen_css = Resource(library, "chosen.css", depends=[chosen_js])
btchosen = Resource(library, "chosen.bootstrap.css", depends=[chosen_css])
chosen_ajax = Resource(library, "chosen.ajaxaddition.jquery.js", depends=[chosen_js])

css = Resource(library, "flg.css")
# responsive = Resource(library, "responsive.css")
# tabs = Resource(library, "tabs.js", depends=[responsive, bootstrap_js, jquery])
js = Resource(library, "flg.js", depends=[jquery])
register_js = Resource(library, "register.js", depends=[jquery])


class FernlehrgangResourceViewlet(grok.Viewlet):
    grok.viewletmanager(IHeaders)
    grok.context(Interface)

    def update(self):
        css.need()
        js.need()

    def render(self):
        return u""
