# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from fernlehrgang import Page
from z3c.saconfig import Session
from megrok.traject import locate
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields
from dolmen.app.layout import models

grok.templatedir('templates')


class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp) 


class Index(models.Index):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Beschreibugn Fernlehrgang"
