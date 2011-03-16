# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.models import Teilnehmer, Kursteilnehmer, Fernlehrgang
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import TablePage, Column, GetAttrColumn, LinkColumn
from uvc.layout.interfaces import IExtraInfo
from z3c.saconfig import Session
from zeam.form.base import Fields


grok.templatedir('templates')


@menuentry(NavigationMenu)
class TeilnehmerListing(TablePage):
    grok.implements(IDisplayView)
    grok.context(IUnternehmen)
    grok.name('teilnehmer_listing')
    grok.title(u'Teilnehmer verwalten')

    template = grok.PageTemplateFile('templates/base_listing.pt')

    label = u"Teilnehmer"

    @property
    def description(self):
        return u"Hier können Sie die Teilnehmer zum Unternehmen '%s %s' verwalten." % (self.context.mnr, self.context.name)

    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.teilnehmer:
            locate(root, x, DefaultModel)
        return self.context.teilnehmer


@menuentry(AddMenu)
class AddTeilnehmer(uvc.layout.AddForm):
    grok.context(IUnternehmen)
    grok.title(u'Teilnehmer')
    label = u'Teilnehmer anlegen für Unternehmen'

    fields = Fields(ITeilnehmer).omit('id')

    def create(self, data):
        lehrgang = data.pop('lehrgang')
        kursteilnehmer = Kursteilnehmer(
            fernlehrgang_id=lehrgang,
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
    label = u"Teilnehmer"

    fields = Fields(ITeilnehmer).omit('id')


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
