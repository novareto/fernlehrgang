# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import uvclight

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
    uvclight.context(ILehrheft)
    uvclight.name('frage_listing')
    uvclight.title(u'Fragen verwalten')
    uvclight.layer(IFernlehrgangSkin)
    
    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Fragen"
    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}

    @property
    def description(self):
        return (u"Hier können Sie die Fragen zu Ihrem Lehrheft " +
                u"'%s' verwalten." % self.context.titel)

    @property
    def values(self):
        root = uvclight.getSite()
        for frage in self.context.fragen:
            locate(root, frage, DefaultModel)
            yield frage


@menuentry(AddMenu)
class AddFrage(AddForm):
    uvclight.context(ILehrheft)
    uvclight.title(u'Frage')
    uvclight.layer(IFernlehrgangSkin)
    
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
    uvclight.name('index')
    uvclight.context(IFrage)
    uvclight.title(u'Frage')
    uvclight.layer(IFernlehrgangSkin)
    
    def update(self):
        view = EmbeddedFrage(self.context, self.request)
        self.frage = view()
        self.parent = view.context.lehrheft
        root = uvclight.getSite()
        locate(root, self.parent, DefaultModel)
        self.link = self.url(self.parent)


@menuentry(NavigationMenu, order=2)
class Edit(Edit):
    uvclight.context(IFrage)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.title(u'Bearbeiten')

    title = u"Fragen"
    description = u"Hier können Sie die Frage bearbeiten."

    fields = Fields(IFrage).omit('id')
    fields['frage'].mode = 'hiddendisplay'


### Spalten

class Id(GetAttrColumn):
    uvclight.name('id')
    uvclight.context(ILehrheft)
    weight = 5 
    header = "Id"
    attrName = "id"


class Nummer(GetAttrColumn):
    uvclight.name('Nummer')
    uvclight.context(ILehrheft)
    weight =  10 
    header = "Nummer"
    attrName = "frage"


class Link(LinkColumn):
    uvclight.name('Titel')
    uvclight.context(ILehrheft)
    weight = 20 
    linkContent = "edit"
    header = "Titel"

    def getLinkContent(self, item):
        return "%s" % (item.titel)


class Antwortschema(GetAttrColumn):
    uvclight.name('Antwortschema')
    uvclight.context(ILehrheft)
    weight = 10
    attrName = 'antwortschema'
    header = u"Antwortschema"


class Gewichtung(GetAttrColumn):
    uvclight.name('Gewichtung')
    uvclight.context(ILehrheft)
    weight = 20
    attrName = 'gewichtung'
    header = u"Gewichtung"
