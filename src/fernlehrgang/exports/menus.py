# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import grok

from zope.interface import Interface
from uvc.menus.components import Menu
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.viewlets import NavEntry
from fernlehrgang.browser import Page


grok.templatedir("templates")


class ExporteNA(NavEntry):
    grok.context(IFernlehrgang)
    grok.order(200)
    grok.name("nav_enty_exp")

    title = u"Versandlisten"
    icon = "fas fa-file-export"

    def url(self):
        return self.view.url(self.context, "exporte")


class Exporte(Page):
    grok.context(IFernlehrgang)


class ExportItems(Menu):
    grok.context(Interface)
    grok.title("ExportItems")
