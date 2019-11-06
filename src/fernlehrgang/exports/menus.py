# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.interface import Interface
from uvc.menus.components import Menu
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.viewlets import NavigationMenu
from fernlehrgang.browser import Page


grok.templatedir('templates')


#@menuentry(NavigationMenu, order=200)
class Exporte(Page):
    grok.context(IFernlehrgang)
    grok.title(u'Versandlisten')
    grok.order(200)
    #grok.require('dolmen.content.Add')


class ExportItems(Menu):
    grok.context(Interface)
    grok.title('ExportItems')
