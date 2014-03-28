# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import uvclight

from dolmen.menu import menuentry, Entry, menu
from fernlehrgang.models import Frage
from uvclight import Page
from zope.location import locate
from uvclight.backends.patterns import DefaultModel
from megrok.z3ctable import TablePage, GetAttrColumn, LinkColumn
from dolmen.forms.base import Fields

from . import AddForm, EditForm
from ..interfaces import IFrage, ILehrheft
from ..wsgi import IFernlehrgangSkin, model_lookup
from .lehrheft import EmbeddedFrage
from .viewlets import AddMenu, NavigationMenu



@menuentry(NavigationMenu)
class FrageListing(uvclight.TablePage):
    uvclight.context(ILehrheft)
    uvclight.name('frage_listing')
    uvclight.title(u'Fragen verwalten')
    uvclight.layer(IFernlehrgangSkin)
    
    template = uvclight.get_template('base_listing.cpt', __file__)

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
            model_lookup.patterns.locate(root, frage, DefaultModel)
            yield frage


@menuentry(AddMenu)
class AddFrage(uvclight.AddForm):
    uvclight.context(ILehrheft)
    uvclight.title(u'Frage')
    uvclight.layer(IFernlehrgangSkin)
    
    label = u'Frage anlegen'
    fields = uvclight.Fields(IFrage).omit('id')

    def create(self, data):
        return Frage(**data)

    def add(self, object):
        self.object = object
        self.context.fragen.append(object)

    def nextURL(self):
        return self.url(self.context, 'frage_listing')


@menuentry(NavigationMenu, order=1)
class FrageIndex(uvclight.Page):
    uvclight.name('index')
    uvclight.context(IFrage)
    uvclight.title(u'Frage')
    uvclight.layer(IFernlehrgangSkin)
    template = uvclight.get_template('frageindex.cpt', __file__)
    
    def update(self):
        view = EmbeddedFrage(self.context, self.request)
        view.update()
        self.frage = view.render()
        self.parent = view.context.lehrheft
        root = uvclight.getSite()
        model_lookup.patterns.locate(root, self.parent, DefaultModel)
        self.link = self.url(self.parent)


@menuentry(NavigationMenu, order=2)
class Edit(uvclight.EditForm):
    uvclight.context(IFrage)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.title(u'Bearbeiten')

    title = u"Fragen"
    description = u"Hier können Sie die Frage bearbeiten."

    fields = uvclight.Fields(IFrage).omit('id')
    #fields['frage'].mode = 'hiddendisplay'


### Spalten

class Id(uvclight.GetAttrColumn):
    uvclight.name('id')
    uvclight.context(ILehrheft)
    weight = 5 
    header = "Id"
    attrName = "id"


class Nummer(uvclight.GetAttrColumn):
    uvclight.name('Nummer')
    uvclight.context(ILehrheft)
    weight =  10 
    header = "Nummer"
    attrName = "frage"


class Link(uvclight.LinkColumn):
    uvclight.name('Titel')
    uvclight.context(ILehrheft)
    weight = 20 
    linkContent = "edit"
    header = "Titel"

    def getLinkContent(self, item):
        return "%s" % (item.titel)


class Antwortschema(uvclight.GetAttrColumn):
    uvclight.name('Antwortschema')
    uvclight.context(ILehrheft)
    weight = 10
    attrName = 'antwortschema'
    header = u"Antwortschema"


class Gewichtung(uvclight.GetAttrColumn):
    uvclight.name('Gewichtung')
    uvclight.context(ILehrheft)
    weight = 20
    attrName = 'gewichtung'
    header = u"Gewichtung"
