# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from megrok.traject import locate
from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.lehrheft import ILehrheft
from megrok.z3ctable import LinkColumn, GetAttrColumn
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from dolmen.app.layout import models, IDisplayView
from zeam.form.base import Fields
from fernlehrgang.interfaces import IListing
from grokcore.chameleon.components import ChameleonPageTemplateFile
from fernlehrgang import AddForm
from uvc.layout import TablePage


grok.templatedir('templates')


@menuentry(NavigationMenu)
class LehrheftListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(IFernlehrgang)
    grok.name('lehrheft_listing')
    grok.title(u'Lehrhefte verwalten')

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Lehrhefte"

    @property
    def description(self):
        return u"Hier können Sie die Lehrhefte zum Fernlehrgang '%s %s' bearbeiten." % (self.context.titel, self.context.jahr)

    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}

    @property
    def values(self):
        root = grok.getSite()
        for x in self.context.lehrhefte:
            locate(root, x, DefaultModel)
        return self.context.lehrhefte


@menuentry(AddMenu)
class AddLehrheft(AddForm):
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


@menuentry(NavigationMenu, order=1)
class Index(models.DefaultView):
    grok.context(ILehrheft)
    grok.name('index')
    grok.title(u'Lehrheft')
    grok.order(51)
    title = label = u"Lehrheft"
    description = u"Details zu Ihrem Lehrheft"
    fields = Fields(ILehrheft).omit(id)


class Edit(models.Edit):
    grok.context(ILehrheft)
    grok.title(u'Edit')
    grok.name('edit')

    label = u"Bearbeiten"

    @property
    def description(self):
        return u"Hier können Sie das '%s' vom Fernlehrgang '%s' bearbeiten." % (
            self.context.titel, 'MUSS')

    fields = Fields(ILehrheft).omit('id')


# Spalten

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
