# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft
from grokcore.chameleon.components import ChameleonPageTemplateFile
from grokcore.view import View
from megrok.layout import Page
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import LinkColumn, GetAttrColumn, TablePage
from zeam.form.base import Fields
from zope.component import getUtility
from zope.interface import Interface, implementer
from zope.security import checkPermission
from zope.security.checker import CheckerPublic

from . import AddForm
from ..interfaces import IListing, IFernlehrgang, IFrage, ILehrheft
from .skin import IFernlehrgangSkin
from .viewlets import AddMenu, NavigationMenu


grok.templatedir('templates')


def check_object_permission(obj, permission):
    if permission == 'zope.Public':
        permission = CheckerPublic
    return checkPermission(permission, obj)


@menuentry(NavigationMenu)
class LehrheftListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(IFernlehrgang)
    grok.name('lehrheft_listing')
    grok.title(u'Lehrhefte verwalten')
    grok.layer(IFernlehrgangSkin)
    
    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Lehrhefte"

    @property
    def description(self):
        return (u"Hier können Sie die Lehrhefte zum Fernlehrgang " +
                u"'%s %s' bearbeiten." %
                (self.context.titel, self.context.jahr))

    cssClasses = {
        'table': 'table table-striped table-bordered table-condensed'}

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
    grok.layer(IFernlehrgangSkin)
    
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


class EmbeddedFrage(View):
    grok.context(IFrage)
    grok.name('embedded')
    grok.layer(IFernlehrgangSkin)

    image = None
    thumb = None

    def __init__(self, context, request):
        root = grok.getSite()
        locate(root, context, DefaultModel)
        View.__init__(self, context, request)

    def update(self):
        self.id = str(self.context.id)
        self.link = self.url(self.context)
        self.editable = check_object_permission(
            self.context, 'dolmen.content.Edit')
        if self.context.bilder.count():
            store = getUtility(Interface, name='ImageStore')
            self.image = self.context.bild.locate(store=store)
            self.thumb = self.context.thumbnail.locate(store=store)

from dolmen.app.layout import ContextualMenu    

@menuentry(ContextualMenu, order=10)
@implementer(IDisplayView)
class LehrheftIndex(Page):
    grok.context(ILehrheft)
    grok.name('index')
    grok.layer(IFernlehrgangSkin)

    def update(self):
        self.fragen = (EmbeddedFrage(frage, self.request)
                       for frage in self.context.fragen)


@menuentry(ContextualMenu, order=20)
class Edit(models.Edit):
    grok.context(ILehrheft)
    grok.title(u'Edit')
    grok.name('edit')
    grok.layer(IFernlehrgangSkin)

    label = u"Bearbeiten"
    fields = Fields(ILehrheft).omit('id')
    
    @property
    def description(self):
        return (u"Hier können Sie das '%s' vom Fernlehrgang "
                u"'%s' bearbeiten." % (self.context.titel, 'MUSS'))


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
