# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

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
from ..wsgi import IFernlehrgangSkin
from .viewlets import AddMenu, NavigationMenu


def check_object_permission(obj, permission):
    if permission == 'zope.Public':
        permission = CheckerPublic
    return checkPermission(permission, obj)


@menuentry(NavigationMenu)
class LehrheftListing(TablePage):
    uvclight.implements(IListing)
    uvclight.context(IFernlehrgang)
    uvclight.name('lehrheft_listing')
    uvclight.title(u'Lehrhefte verwalten')
    uvclight.layer(IFernlehrgangSkin)
    
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
        root = uvclight.getSite()
        for x in self.context.lehrhefte:
            locate(root, x, DefaultModel)
        return self.context.lehrhefte


@menuentry(AddMenu)
class AddLehrheft(AddForm):
    uvclight.context(IFernlehrgang)
    uvclight.title(u'Lehrheft')
    uvclight.layer(IFernlehrgangSkin)
    
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
    uvclight.context(IFrage)
    uvclight.name('embedded')
    uvclight.layer(IFernlehrgangSkin)

    image = None
    thumb = None

    def __init__(self, context, request):
        root = uvclight.getSite()
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
  

@menuentry(ContextualMenu, order=10)
class LehrheftIndex(Page):
    uvclight.context(ILehrheft)
    uvclight.name('index')
    uvclight.layer(IFernlehrgangSkin)

    def update(self):
        self.fragen = (EmbeddedFrage(frage, self.request)
                       for frage in self.context.fragen)


@menuentry(ContextualMenu, order=20)
class Edit(models.Edit):
    uvclight.context(ILehrheft)
    uvclight.title(u'Edit')
    uvclight.name('edit')
    uvclight.layer(IFernlehrgangSkin)

    label = u"Bearbeiten"
    fields = Fields(ILehrheft).omit('id')
    
    @property
    def description(self):
        return (u"Hier können Sie das '%s' vom Fernlehrgang "
                u"'%s' bearbeiten." % (self.context.titel, 'MUSS'))


## Spalten

class Id(GetAttrColumn):
    uvclight.name('id')
    uvclight.context(IFernlehrgang)
    weight = 5 
    attrName = "id"
    header = "Id"


class Nummer(GetAttrColumn):
    uvclight.name('nummer')
    uvclight.context(IFernlehrgang)
    weight = 10
    attrName = "nummer"
    header = "Nummer"


class Name(LinkColumn):
    uvclight.name('Nummer')
    uvclight.context(IFernlehrgang)
    weight = 99
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.titel
