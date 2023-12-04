# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from uvc.menus.components import MenuItem
from uvc.menus.directives import menu
from megrok.traject import locate
from fernlehrgang.models import Frage
from fernlehrgang.interfaces.frage import IFrage
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3ctable import GetAttrColumn, LinkColumn
from fernlehrgang.viewlets import NavigationMenu
from zeam.form.base import Fields
from grokcore.chameleon.components import ChameleonPageTemplateFile
from fernlehrgang.browser import AddForm, TablePage, DefaultView, EditForm
from fernlehrgang.viewlets import AddEntry
from fernlehrgang.viewlets import NavEntry


grok.templatedir("templates")


class FRNavEntry(NavEntry):
    grok.context(IFrage)
    grok.order(30)
    grok.name("fr-nav-entry")

    title = "Frage"

    def url(self):
        return self.view.url(self.context)


class FRNavEntry1(FRNavEntry):
    grok.context(ILehrheft)
    grok.order(40)
    title = "Fragen"

    def url(self):
        return self.view.url(self.context, "frage_listing")


# @menuentry(NavigationMenu, order=20)
class FrageListing(TablePage):
    grok.context(ILehrheft)
    grok.name("frage_listing")
    grok.title("Fragen verwalten")
    grok.order(20)

    template = ChameleonPageTemplateFile("templates/base_listing.cpt")

    label = "Fragen"
    cssClasses = {"table": "table table-striped table-bordered table-condensed"}

    @property
    def description(self):
        return (
            "Hier können Sie die Fragen zu                Ihrem Lehrheft '%s'"
            " verwalten." % self.context.titel
        )

    def getSortOn(self):
        return "table-Nummer-1"

    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.fragen:
            locate(root, x, DefaultModel)
        dd = sorted(self.context.fragen, key=lambda x: int(x.frage))
        return dd


class AddEntryFrage(AddEntry):
    grok.context(ILehrheft)
    grok.name("addentryFrage")
    grok.require("zope.View")
    title = "Frage"

    def url(self):
        return self.view.url(self.context, "addfrage")


# @menuentry(AddMenu)
class AddFrage(AddForm):
    grok.context(ILehrheft)
    grok.title("Frage")
    label = "Frage anlegen"

    fields = Fields(IFrage).omit("id")

    def create(self, data):
        return Frage(**data)

    def add(self, object):
        self.object = object
        self.context.fragen.append(object)

    def nextURL(self):
        return self.url(self.context, "frage_listing")


class HelperEntry(MenuItem):
    grok.context(IFrage)
    grok.name("index")
    grok.title("Frage")
    grok.order(1)
    menu(NavigationMenu)


# @menuentry(NavigationMenu)
class Index(DefaultView):
    grok.context(IFrage)
    grok.title("Ansicht")
    grok.order(10)
    title = label = "Frage"
    description = "Hier können Sie Deteils zu Ihren Fragen ansehen."

    fields = Fields(IFrage).omit("id")


class Edit(EditForm):
    grok.context(IFrage)
    grok.title("Bearbeiten")
    grok.name("edit")

    title = "Fragen"
    description = "Hier können Sie die Frage bearbeiten."
    fields = Fields(IFrage).omit("id")
    fields["frage"].mode = "hiddendisplay"


# Spalten


class Id(GetAttrColumn):
    grok.name("id")
    grok.context(ILehrheft)
    weight = 5
    header = "Id"
    attrName = "id"


class Nummer(GetAttrColumn):
    grok.name("Nummer")
    grok.context(ILehrheft)
    weight = 10
    header = "Nummer"
    attrName = "frage"

    def getSortKey(self, item):
        return int(super(Nummer, self).getSortKey(item))


class Link(LinkColumn):
    grok.name("Titel")
    grok.context(ILehrheft)
    weight = 20
    linkContent = "edit"
    header = "Titel"

    def getLinkContent(self, item):
        return "%s" % (item.titel)


class Antwortschema(GetAttrColumn):
    grok.name("Antwortschema")
    grok.context(ILehrheft)
    weight = 10
    attrName = "antwortschema"
    header = "Antwortschema"


class Gewichtung(GetAttrColumn):
    grok.name("Gewichtung")
    grok.context(ILehrheft)
    weight = 20
    attrName = "gewichtung"
    header = "Gewichtung"
