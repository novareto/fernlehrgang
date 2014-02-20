# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry, Entry, menu
from fernlehrgang.models import Frage
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.layout import Page
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import TablePage, GetAttrColumn, LinkColumn
from zeam.form.base import Fields

from . import AddForm
from ..interfaces import IFrage, ILehrheft
from .lehrheft import EmbeddedFrage
from .skin import IFernlehrgangSkin
from .viewlets import AddMenu, NavigationMenu

grok.templatedir('templates')


@menuentry(NavigationMenu)
class FrageListing(TablePage):
    grok.implements(IDisplayView)
    grok.context(ILehrheft)
    grok.name('frage_listing')
    grok.title(u'Fragen verwalten')
    grok.layer(IFernlehrgangSkin)
    
    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Fragen"
    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}

    @property
    def description(self):
        return (u"Hier können Sie die Fragen zu Ihrem Lehrheft " +
                u"'%s' verwalten." % self.context.titel)

    @property
    def values(self):
        root = grok.getSite()
        for frage in self.context.fragen:
            locate(root, frage, DefaultModel)
            yield frage


@menuentry(AddMenu)
class AddFrage(AddForm):
    grok.context(ILehrheft)
    grok.title(u'Frage')
    grok.layer(IFernlehrgangSkin)
    
    label = u'Frage anlegen'
    fields = Fields(IFrage).omit('id')

    def create(self, data):
        return Frage(**data)

    def add(self, object):
        self.object = object
        self.context.fragen.append(object)

    def nextURL(self):
        return self.url(self.context, 'frage_listing')


@menuentry(NavigationMenu, order=1)
class FrageIndex(Page):
    grok.name('index')
    grok.context(IFrage)
    grok.title(u'Frage')
    grok.layer(IFernlehrgangSkin)
    
    def update(self):
        view = EmbeddedFrage(self.context, self.request)
        self.frage = view()
        self.parent = view.context.lehrheft
        root = grok.getSite()
        locate(root, self.parent, DefaultModel)
        self.link = self.url(self.parent)


@menuentry(NavigationMenu, order=2)
class Edit(models.Edit):
    grok.context(IFrage)
    grok.layer(IFernlehrgangSkin)
    grok.title(u'Bearbeiten')

    title = u"Fragen"
    description = u"Hier können Sie die Frage bearbeiten."

    fields = Fields(IFrage).omit('id')
    fields['frage'].mode = 'hiddendisplay'


### Spalten

class Id(GetAttrColumn):
    grok.name('id')
    grok.context(ILehrheft)
    weight = 5 
    header = "Id"
    attrName = "id"


class Nummer(GetAttrColumn):
    grok.name('Nummer')
    grok.context(ILehrheft)
    weight =  10 
    header = "Nummer"
    attrName = "frage"


class Link(LinkColumn):
    grok.name('Titel')
    grok.context(ILehrheft)
    weight = 20 
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
