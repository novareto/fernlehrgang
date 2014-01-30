# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from megrok.traject.components import DefaultModel

class DynamicDefaultModelView(grok.View):
    grok.name('index')
    grok.context(DefaultModel)

    def render(self):
        view_name = self.context.__name__ + '_listing'
        self.redirect(self.url(self.context.__parent__, view_name))
