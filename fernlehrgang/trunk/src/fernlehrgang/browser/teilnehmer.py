# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.models import Teilnehmer, Kursteilnehmer, Fernlehrgang 
from uvc.layout.interfaces import ISidebar, IExtraInfo
from megrok.traject.components import DefaultModel
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from megrok.z3ctable import Column, GetAttrColumn, CheckBoxColumn, LinkColumn
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from megrok.z3cform.base.directives import cancellable
from dolmen.app.layout import models, ContextualMenuEntry

from dolmen.menu import menuentry
from fernlehrgang.ui_components import AddMenu, NavigationMenu

grok.templatedir('templates')

@menuentry(NavigationMenu)
class TeilnehmerListing(DeleteFormTablePage):
    grok.context(IUnternehmen)
    grok.name('teilnehmer_listing')
    grok.title(u'Teilnehmer verwalten')

    template = grok.PageTemplateFile('templates/base_listing.pt')

    title = u"Teilnehmer"

    @property
    def description(self):
        return u"Hier können Sie die Teilnehmer zum Unternehmen '%s %s' verwalten." %(self.context.mnr, self.context.name)

    extends(DeleteFormTablePage)
    cssClasses = {'table': 'tablesorter myTable'}

    status = None

    @property
    def values(self):
        root = getSite()
        for x in self.context.teilnehmer:
            locate(root, x, DefaultModel)
        return self.context.teilnehmer

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.flash(u'Der Teilnehmer wurde erfolgreich gelöscht.')
        self.nextURL = self.url(self.context, 'teilnehmer_listing')
        self.request.response.redirect(self.nextURL)

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True

    @button.buttonAndHandler(u'Teilnehmer anlegen')
    def handleChangeWorkflowState(self, action):
         self.redirect(self.url(self.context, 'addteilnehmer')) 


@menuentry(AddMenu)
class AddTeilnehmer(PageAddForm):
    grok.context(IUnternehmen)
    grok.title(u'Teilnehmer')
    title = u'Teilnehmer'
    label = u'Teilnehmer anlegen für Unternehmen'
    cancellable(True)

    fields = Fields(ITeilnehmer).omit('id')

    def create(self, data):
        lehrgang = data.pop('lehrgang')
        kursteilnehmer = Kursteilnehmer(
            fernlehrgang_id = lehrgang, 
            status="A1", 
            unternehmen_mnr=self.context.mnr)
        teilnehmer = Teilnehmer(**data)
        return (kursteilnehmer, teilnehmer)

    def add(self, object):
        kursteilnehmer, teilnehmer = object
        session = Session()
        self.context.teilnehmer.append(teilnehmer)
        kursteilnehmer.teilnehmer = teilnehmer
        kursteilnehmer.unternehmen = self.context
        if kursteilnehmer.fernlehrgang_id:
            fernlehrgang = session.query(Fernlehrgang).filter( Fernlehrgang.id == kursteilnehmer.fernlehrgang_id).one()
            fernlehrgang.kursteilnehmer.append(kursteilnehmer)

    def nextURL(self):
        return self.url(self.context, 'teilnehmer_listing')



class Index(models.DefaultView):
    grok.context(ITeilnehmer)
    title = label = u"Teilnehmer"
    description = u"Details zu Ihrem Unternehmen"

    fields = Fields(ITeilnehmer).omit(id)


class Edit(models.Edit):
    grok.context(ITeilnehmer)
    grok.name('edit')
    extends(PageEditForm)
    title = label = u"Teilnehmer"

    fields = Fields(ITeilnehmer).omit('id')

    @button.buttonAndHandler(u'Teilnehmer entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.redirect(self.url(self.context.__parent__)) 


# More Info Viewlets

class MoreInfoUnternehmen(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IUnternehmen) 

    def render(self):
        return "<h3>Mitgliedsnummer: %s, Unternehmen: %s </h3>" %(self.context.mnr, self.context.name)

class MoreInfoOnTeilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(ITeilnehmer)

    def render(self):
        return "<h3>Mitgliedsnummer: %s, Unternehmen: %s </h3>" %(self.context.unternehmen.mnr, self.context.unternehmen.name)

## Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IUnternehmen)
    weight = 0
    cssClasses = {'th': 'checkBox'}
    

class Name(LinkColumn):
    grok.name('Name')
    grok.context(IUnternehmen)
    weight = 10 
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.name


class VorName(GetAttrColumn):
    grok.name('VorName')
    grok.context(IUnternehmen)
    weight = 20 
    header = u"Vorname"
    attrName = "vorname"


class Geburtsdatum(Column):    
    grok.name('Geburtsdatum')
    grok.context(IUnternehmen)
    weight = 30 
    header = u"Geburtsdatum"

    def renderCell(self, item):
        if item.geburtsdatum != None:
            return item.geburtsdatum.strftime('%d.%m.%Y')
        return ""
