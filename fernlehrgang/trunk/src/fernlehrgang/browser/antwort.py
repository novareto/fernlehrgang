# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from dolmen.app.layout import models
from fernlehrgang.utils import Page
from fernlehrgang.models import Antwort, Frage 
from fernlehrgang.utils import MenuItem
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from uvc.layout.interfaces import ISidebar
from fernlehrgang.interfaces.antwort import IAntwort
from megrok.traject.components import DefaultModel
from megrok.z3ctable.ftests import Container, Content
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable.components import GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends

from dolmen.app.layout import IDisplayView, ContextualMenuEntry

grok.templatedir('templates')


@menuentry(AddMenu)
class AddAntwort(PageAddForm):
    grok.context(IKursteilnehmer)
    title = u'Antwort'
    label = u'Antwort anlegen'

    fields = Fields(IAntwort).omit('id')

    def create(self, data):
        return Antwort(**data)

    def add(self, object):
        self.object = object
        self.context.antworten.append(object)

    def nextURL(self):
        return self.url(self.context, 'antwort_listing')


class Index(models.DefaultView):
    grok.context(IAntwort)
    grok.title(u'Index')
    title = label = u"Antwort"
    description = u"Hier können Sie Deteils zu Ihren Antworten ansehen."

    fields = Fields(IAntwort).omit('id')


class Edit(models.Edit):
    grok.context(IAntwort)
    grok.title(u'Edit')
    grok.name('edit')
    title = u"Antworten"
    description = u"Hier können Sie die Antwort bearbeiten."

    extends(PageEditForm)
    fields = Fields(IAntwort).omit('id')

    @button.buttonAndHandler(u'Fernlehrgang entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 

@menuentry(NavigationMenu)
class AntwortListing(DeleteFormTablePage):
    grok.context(IKursteilnehmer)
    grok.name('antwort_listing')
    grok.title(u'Antworten verwalten')
    title = u"Antworten"
    description = u"Hier können Sie die Antworten zu Ihren Lehrheften bearbeiten."
    extends(DeleteFormTablePage)

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.antworten:
            locate(root, x, DefaultModel)
        return self.context.antworten

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.nextURL = self.url(self.context, 'antwort_listing')

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

    @button.buttonAndHandler(u'Antwort anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addantwort')) 


class JSON_Views(grok.JSON):
    """ Ajax basiertes Wechseln der Jahre"""
    grok.context(IKursteilnehmer)
 
    def context_fragen(self, lehrheft_id=None):
        rc = []
        session = Session()
        i=0
        for id, nr, titel in session.query(Frage.id, Frage.frage, Frage.titel).filter(
                                           Frage.lehrheft_id == int(lehrheft_id)).all():
            rc.append('<option id="form-widgets-frage_id-%s" value=%s> %s - %s </option>' %(i, id, nr, titel))
            i+=1
        return {'fragen': ''.join(rc)}


### Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IKursteilnehmer)
    weight = 0


class Link(LinkColumn):
    grok.name('Nummer')
    grok.context(IKursteilnehmer)
    weight = 5 
    linkContent = "edit"

    def getLinkContent(self, item):
        return u"Antwort für Frage %s" %item.id

class Antworten(GetAttrColumn):
    grok.name('Antworten')
    grok.context(IKursteilnehmer)
    weight = 10
    header = "Antworten"
    attrName = "antwortschema"


