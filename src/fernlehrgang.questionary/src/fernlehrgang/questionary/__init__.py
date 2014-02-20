# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from dolmen.forms.crud import Add
from uvclight import Form


class Form(Form):
    grok.require('dolmen.content.Add')
    grok.baseclass()


class AddForm(Form):
    grok.require('dolmen.content.Add')
    grok.baseclass()
