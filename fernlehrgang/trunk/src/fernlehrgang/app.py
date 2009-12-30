# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from megrok.traject import locate
from fernlehrgang import Page
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.fernlehrgang import IFernlehrgang

from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields
from z3c.saconfig import Session

grok.templatedir('templates')

class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp) 


class Index(Page):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Fernlehrgang"

    def getFernlehrgaenge(self):
        session = Session()
        return session.query(Fernlehrgang).all() 

    def createLink(self, name):
        return "%s/fernlehrgang/%s" % (self.url(self.context), name)
