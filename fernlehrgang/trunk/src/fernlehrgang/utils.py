# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from megrok.layout import Page as basePage
from z3c.menu.simple.menu import GlobalMenuItem
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class MenuItem(grok.Viewlet, GlobalMenuItem):
    grok.baseclass()
    template = ViewPageTemplateFile('templates/menu_item.pt')

    def render(self):
        return self.template()


class Page(basePage, grok.View):
    grok.baseclass()
