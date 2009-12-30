# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from megrok.traject import locate
from fernlehrgang.utils import Page
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Lehrheft 
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang

from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields
from z3c.saconfig import Session

grok.templatedir('templates')


class AddLehrheft(PageAddForm, grok.View):
    grok.context(IFernlehrgang)
    title = u'Lehrheft'
    label = u'Lehrheft anlegen'

    fields = Fields(ILehrheft).omit('id')

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.context.lehrhefte.append(object)

    def nextURL(self):
        url = "http://localhost:8080/flg/fernlehrgang/1"
        #url = self.url(self.context)
        return url

class Lehrhefte(PageDisplayForm, grok.View):
    grok.context(IFernlehrgang)
    grok.name('lehrhefte')

    fields = Fields(ILehrheft).omit('id')
