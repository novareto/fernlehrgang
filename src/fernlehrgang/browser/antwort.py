# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from dolmen.app.layout import models
from megrok.layout import Page
from fernlehrgang.models import Antwort, Frage 
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from uvc.layout.interfaces import ISidebar
from fernlehrgang.interfaces.antwort import IAntwort
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable.components import GetAttrColumn, CheckBoxColumn, LinkColumn, Column
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from megrok.z3cform.base.directives import cancellable
from sqlalchemy import not_, and_

from dolmen.app.layout import IDisplayView, ContextualMenuEntry

grok.templatedir('templates')


@menuentry(NavigationMenu)
class AntwortListing(DeleteFormTablePage):
    grok.context(IKursteilnehmer)
    grok.name('antwort_listing')
    grok.title(u'Antworten verwalten')

    template = grok.PageTemplateFile('templates/base_listing.pt')

    title = u"Antworten"
    description = u"Hier können Sie die Antworten zu Ihren Lehrheften bearbeiten."

    extends(DeleteFormTablePage)
    cssClasses = {'table': 'tablesorter myTable'}

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
        self.flash(u'Die Antwort wurde erfolgreich gelöscht.')
        self.nextURL = self.url(self.context, 'antwort_listing')
        self.request.response.redirect(self.nextURL)

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


@menuentry(AddMenu)
class AddAntwort(PageAddForm):
    grok.context(IKursteilnehmer)
    grok.title(u'Antwort')
    title = u'Antwort'
    label = u'Antwort anlegen'
    cancellable(True)

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

    @button.buttonAndHandler(u'Antwort entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 


class JSON_Views(grok.JSON):
    """ Ajax basiertes Wechseln der Jahre"""
    grok.context(IKursteilnehmer)
 
    def context_fragen(self, lehrheft_id=None):
        rc = []
        li = []
        session = Session()
        i=0
        print "Lehrheft_id", lehrheft_id
        for antwort in [x for x in self.context.antworten]:
            li.append(antwort.frage.id)
        for id, nr, titel in session.query(Frage.id, Frage.frage, Frage.titel).filter(
                                           and_(Frage.lehrheft_id == int(lehrheft_id),
                                                not_(Frage.id.in_(li)))).all():
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
        return u"Antwort für Frage %s Lehrheft %s" %(item.frage.titel, item.frage.lehrheft.titel)

class Lehrheft(Column):
    grok.name('Lehrheft')
    grok.context(IKursteilnehmer)
    weight = 9 
    header = "Lehrheft"

    def renderCell(self, item):
        return item.frage.lehrheft.title

class Antworten(GetAttrColumn):
    grok.name('Antworten')
    grok.context(IKursteilnehmer)
    weight = 10
    header = "Antworten"
    attrName = "antwortschema"
