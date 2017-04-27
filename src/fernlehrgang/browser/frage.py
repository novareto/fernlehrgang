# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from megrok.traject import locate
from fernlehrgang.models import Frage
from fernlehrgang.interfaces.frage import IFrage
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3ctable import GetAttrColumn, LinkColumn
from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry, Entry, menu
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from zeam.form.base import Fields
from grokcore.chameleon.components import ChameleonPageTemplateFile
from fernlehrgang import AddForm
from uvc.layout import TablePage


grok.templatedir('templates')


@menuentry(NavigationMenu, order=20)
class FrageListing(TablePage):
    grok.implements(IDisplayView)
    grok.context(ILehrheft)
    grok.name('frage_listing')
    grok.title(u'Fragen verwalten')
    grok.order(20)

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Fragen"
    cssClasses = {
        'table': 'table table-striped table-bordered table-condensed'}

    @property
    def description(self):
        return u"Hier können Sie die Fragen zu\
                Ihrem Lehrheft '%s' verwalten." % self.context.titel

    def getSortOn(self):
        return "table-Nummer-1"

    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.fragen:
            locate(root, x, DefaultModel)
        return self.context.fragen


@menuentry(AddMenu)
class AddFrage(AddForm):
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


class HelperEntry(Entry):
    grok.context(IFrage)
    grok.name('index')
    grok.title('Frage')
    grok.order(1)
    menu(NavigationMenu)


@menuentry(NavigationMenu)
class Index(models.DefaultView):
    grok.context(IFrage)
    grok.title(u'Ansicht')
    grok.order(10)
    title = label = u"Frage"
    description = u"Hier können Sie Deteils zu Ihren Fragen ansehen."

    fields = Fields(IFrage).omit('id')


class Edit(models.Edit):
    grok.context(IFrage)
    grok.title(u'Bearbeiten')
    grok.name('edit')
    title = u"Fragen"
    description = u"Hier können Sie die Frage bearbeiten."

    fields = Fields(IFrage).omit('id')
    fields['frage'].mode = 'hiddendisplay'


# Spalten

class Id(GetAttrColumn):
    grok.name('id')
    grok.context(ILehrheft)
    weight = 5
    header = "Id"
    attrName = "id"


class Nummer(GetAttrColumn):
    grok.name('Nummer')
    grok.context(ILehrheft)
    weight = 10
    header = "Nummer"
    attrName = "frage"

    def getSortKey(self, item):
        return int(super(Nummer, self).getSortKey(item))


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
