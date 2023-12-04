# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang.browser import AddForm, TablePage, EditForm, DefaultView
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.lehrheft import ILehrheft
from fernlehrgang.models import Lehrheft
from fernlehrgang.viewlets import NavEntry
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import LinkColumn, GetAttrColumn
from zeam.form.base import Fields
from zope.interface import implementer
from fernlehrgang.viewlets import AddEntry


grok.templatedir("templates")


class LHNavEntry(NavEntry):
    grok.context(ILehrheft)
    grok.order(30)
    grok.name("lh-nav-entry")

    title = "Lehrheft"

    def url(self):
        return self.view.url(self.context)


class LHNavEntry1(LHNavEntry):
    grok.context(IFernlehrgang)
    title = "Lehrhefte"

    def url(self):
        return self.view.url(self.context, "lehrheft_listing")


@implementer(IListing)
class LehrheftListing(TablePage):
    grok.context(IFernlehrgang)
    grok.name("lehrheft_listing")
    grok.title("Lehrhefte verwalten")

    template = ChameleonPageTemplateFile("templates/base_listing.cpt")

    label = "Lehrhefte"

    @property
    def description(self):
        return "Hier können Sie die Lehrhefte zum Fernlehrgang '%s %s' bearbeiten." % (
            self.context.titel,
            self.context.jahr,
        )

    cssClasses = {"table": "table table-striped table-bordered table-condensed"}

    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.lehrhefte:
            locate(root, x, DefaultModel)
        return self.context.lehrhefte


class AddEntryLH(AddEntry):
    grok.context(IFernlehrgang)
    grok.name("addentryLH")
    grok.require("zope.View")
    title = "Lehrheft"

    def url(self):
        return self.view.url(self.context, "addlehrheft")


class AddLehrheft(AddForm):
    grok.context(IFernlehrgang)
    grok.title("Lehrheft")

    title = "Lehrheft"
    label = "Lehrhefte"
    description = "Hier können Sie die Lehrhefte für den Fernlehrgang anlegen."

    fields = Fields(ILehrheft).omit("id")

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.object = object
        self.context.lehrhefte.append(object)

    def nextURL(self):
        self.flash("Das Lehrheft wurde erfolgreich angelegt")
        return self.url(self.context, "lehrheft_listing")


class Index(DefaultView):
    grok.context(ILehrheft)
    grok.name("index")
    grok.title("Lehrheft")
    grok.order(51)

    title = label = "Lehrheft"
    description = "Details zu Ihrem Lehrheft"
    fields = Fields(ILehrheft).omit(id)


class Edit(EditForm):
    grok.context(ILehrheft)
    grok.title("Edit")
    grok.name("edit")

    label = "Bearbeiten"

    @property
    def description(self):
        return "Hier können Sie das '%s' vom Fernlehrgang '%s' bearbeiten." % (
            self.context.titel,
            "MUSS",
        )

    fields = Fields(ILehrheft).omit("id")


class Id(GetAttrColumn):
    grok.name("id")
    grok.context(IFernlehrgang)

    weight = 5
    attrName = "id"
    header = "Id"


class Nummer(GetAttrColumn):
    grok.name("nummer")
    grok.context(IFernlehrgang)

    weight = 10
    attrName = "nummer"
    header = "Nummer"


class Name(LinkColumn):
    grok.name("Nummer")
    grok.context(IFernlehrgang)

    weight = 99
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.titel
