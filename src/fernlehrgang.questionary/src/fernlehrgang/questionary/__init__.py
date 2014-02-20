# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from uvc.layout.forms.components import AddForm, Form


class Form(Form):
    grok.require('dolmen.content.Add')
    grok.baseclass()


class AddForm(AddForm):
    grok.require('dolmen.content.Add')
    grok.baseclass()
