# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from fernlehrgang import Page
from z3c.saconfig import Session
from dolmen.menu import menuentry
from megrok.traject import locate
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.ui_components.viewlets import AboveContent 
from megrok.z3cform.base import PageDisplayForm, PageAddForm, Fields


grok.templatedir('templates')


class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp) 

from megrok.layout import Page
@menuentry(AboveContent, title=u"Startseite", order=10)
class Index(Page):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgang"
    description = u"Beschreibugn Fernlehrgang"

