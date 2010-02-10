# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from fernlehrgang.models import Teilnehmer 
from megrok.layout import Page as basePage
from z3c.menu.simple.menu import GlobalMenuItem
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class MenuItem(grok.Viewlet, GlobalMenuItem):
    grok.baseclass()
    template = ViewPageTemplateFile('templates/menu_item.pt')

    def render(self):
        return self.template()


class Page(basePage, grok.View):
    grok.baseclass()


### Vocabularies


def vocabulary(*terms):
    """ """
    return SimpleVocabulary([SimpleTerm(value, token, title) for value, token, title in terms])


class UnternehmenSources(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'unternehmen')
    
    def __call__(self, context):
        rc = []
        session = Session()
        for id, name, vorname in session.query(Teilnehmer.id, Teilnehmer.name, Teilnehmer.vorname).all():
            value = "%s - %s %s" % (id, name, vorname)
            rc.append(SimpleTerm(id, value, value))
        return SimpleVocabulary(rc)    
