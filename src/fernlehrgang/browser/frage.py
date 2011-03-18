# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
import uvc.layout

from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.models import Frage 
from uvc.layout.interfaces import ISidebar
from fernlehrgang.interfaces.frage import IFrage
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3ctable import TablePage, GetAttrColumn, CheckBoxColumn, LinkColumn
from dolmen.app.layout import models, IDisplayView 
from dolmen.menu import menuentry
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from zeam.form.base import Fields


grok.templatedir('templates')

@menuentry(NavigationMenu)
class FrageListing(TablePage):
    grok.implements(IDisplayView)
    grok.context(ILehrheft)
    grok.name('frage_listing')
    grok.title(u'Fragen verwalten')

    template = grok.PageTemplateFile('templates/base_listing.pt')

    label = u"Fragen"
    description = u"Hier können Sie die Fragen zu Ihren Lehrheften bearbeiten."
    cssClasses = {'table': 'tablesorter myTable'}


    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.fragen:
            locate(root, x, DefaultModel)
        return self.context.fragen


@menuentry(AddMenu)
class AddFrage(uvc.layout.AddForm):
    grok.context(ILehrheft)
    grok.title(u'Frage')
    label = u'Frage anlegen'

    fields = Fields(IFrage).omit('id')

    def create(self, data):
        return Frage(**data)

    def add(self, object):
        self.object = object
        self.context.fragen.append(object)

    def nextURL(self):
        return self.url(self.context, 'frage_listing')


class Index(models.DefaultView):
    grok.context(IFrage)
    grok.title(u'View')
    title = label = u"Frage"
    description = u"Hier können Sie Deteils zu Ihren Fragen ansehen."

    fields = Fields(IFrage).omit('id')


class Edit(models.Edit):
    grok.context(IFrage)
    grok.title(u'Edit')
    grok.name('edit')
    title = u"Fragen"
    description = u"Hier können Sie die Frage bearbeiten."

    fields = Fields(IFrage).omit('id')


### Spalten

class Nummer(GetAttrColumn):
    grok.name('Nummer')
    grok.context(ILehrheft)
    weight = 3 
    header = "Nummer"
    attrName = "frage"


class Link(LinkColumn):
    grok.name('Titel')
    grok.context(ILehrheft)
    weight = 5 
    linkContent = "edit"
    header = "Titel"

    def getLinkContent(self, item):
        return "%s" % (item.titel)


class Antwortschema(GetAttrColumn):
    grok.name('Antwortschema')
    grok.context(ILehrheft)
    weight = 10
    attrName = 'antwortschema'
    header = u"Antwortschema"


class Gewichtung(GetAttrColumn):
    grok.name('Gewichtung')
    grok.context(ILehrheft)
    weight = 20
    attrName = 'gewichtung'
    header = u"Gewichtung"

