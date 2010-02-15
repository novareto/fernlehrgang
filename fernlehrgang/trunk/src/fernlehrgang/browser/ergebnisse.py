# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.utils import Page
from fernlehrgang.models import Antwort, Frage 
from fernlehrgang.utils import MenuItem 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.interfaces.antwort import IAntwort
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.ui_components.viewlets import AboveContent
from megrok.z3ctable import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends


grok.templatedir('templates')


@menuentry(AboveContent, title=u"Resultate", order=30)
class Resultate(Page):
    grok.context(IKursteilnehmer)
    grok.name('resultate')
    title = u"Resultate"
    description = u"Hier Können Sie die Resultate des Kursteilnehmers einsehen"


    @property
    def lehrhefte(self):
        rc = [] 
        for lehrheft in self.context.fernlehrgang.lehrhefte:
            res = {}
            res['titel'] = "%s - %s" %(lehrheft.nummer, lehrheft.titel)
            lehrheft_id = lehrheft.id
            fragen = []
            for antwort in self.context.antworten: 
                if antwort.frage.lehrheft_id == lehrheft_id:
                    titel = "%s - %s" %(antwort.frage.frage, antwort.frage.titel)
                    d=dict(titel = titel,
                           frage = antwort.frage.antwortschema,
                           antwort = antwort.antwortschema,
                           res = self.calculateResult(antwort.antwortschema, antwort.frage.antwortschema))
                    fragen.append(d)
            res['antworten'] = fragen
            rc.append(res)
        print rc    
        return rc    




    def calculateResult(self, antworten, antwortschema):
        if len(antworten) != len(antwortschema):
            return False
        antwortschema = list(antwortschema)
        for x in antworten:
            if x not in antwortschema:
                return False
        return True        
