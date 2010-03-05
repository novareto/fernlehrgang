# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from fernlehrgang.models import Teilnehmer 
from fernlehrgang.interfaces.antwort import IAntwort 
from fernlehrgang.interfaces.frage import IFrage
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.layout import Page 
from z3c.menu.simple.menu import GlobalMenuItem
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class MenuItem(grok.Viewlet, GlobalMenuItem):
    grok.baseclass()
    template = ViewPageTemplateFile('templates/menu_item.pt')

    def render(self):
        return self.template()

