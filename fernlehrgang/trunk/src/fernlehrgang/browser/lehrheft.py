# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3ctable import (TablePage,
    CheckBoxColumn, LinkColumn, GetAttrColumn)
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from dolmen.app.layout import models, IDisplayView
from zeam.form.base import Fields
from fernlehrgang.interfaces import IListing

grok.templatedir('templates')


@menuentry(NavigationMenu)
class LehrheftListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(IFernlehrgang)
    grok.name('lehrheft_listing')
    grok.title(u'Lehrhefte verwalten')

    template = grok.PageTemplateFile('templates/base_listing.pt')

    label = u"Lehrhefte"

    @property
    def description(self):
        return u"Hier können Sie die Lehrhefte zum Fernlehrgang '%s %s' bearbeiten." % (self.context.titel, self.context.jahr)

    cssClasses = {'table': 'tablesorter myTable'}

    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.lehrhefte:
            locate(root, x, DefaultModel)
        return self.context.lehrhefte


@menuentry(AddMenu)
class AddLehrheft(uvc.layout.AddForm):
    grok.context(IFernlehrgang)
    grok.title(u'Lehrheft')
    title = u'Lehrheft'
    label = u'Lehrhefte'
    description = u'Hier können Sie die Lehrhefte für den Fernlehrgang anlegen.'

    fields = Fields(ILehrheft).omit('id')

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.object = object
        self.context.lehrhefte.append(object)

    def nextURL(self):
        self.flash(u'Das Lehrheft wurde erfolgreich angelegt')
        return self.url(self.context, 'lehrheft_listing')


class Index(models.DefaultView):
    grok.context(ILehrheft)
    grok.name('index')
    title = label = u"Lehrheft"
    description = u"Details zu Ihrem Lehrheft"
    fields = Fields(ILehrheft).omit(id)


class Edit(models.Edit):
    grok.context(ILehrheft)
    grok.title(u'Edit')
    grok.name('edit')

    fields = Fields(ILehrheft).omit('id')


## Spalten

class Id(GetAttrColumn):
    grok.name('id')
    grok.context(IFernlehrgang)
    weight = 5 
    attrName = "id"
    header = "Id"


class Nummer(GetAttrColumn):
    grok.name('nummer')
    grok.context(IFernlehrgang)
    weight = 10
    attrName = "nummer"
    header = "Nummer"


class Name(LinkColumn):
    grok.name('Nummer')
    grok.context(IFernlehrgang)
    weight = 99
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.titel
