# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from dolmen.menu import menuentry
from fernlehrgang.models import Lehrheft
from uvclight import View, Page
from uvclight.backends.patterns import DefaultModel
from megrok.z3ctable import LinkColumn, GetAttrColumn, TablePage
from dolmen.forms.base import Fields
from sqlalchemy_imageattach import context as store
from zope.component import getUtility
from zope.interface import Interface, implementer
from zope.security import checkPermission
from zope.security.checker import CheckerPublic

from . import AddForm, EditForm, pagetemplate
from ..interfaces import IListing, IFernlehrgang, IFrage, ILehrheft
from ..wsgi import IFernlehrgangSkin, model_lookup
from .viewlets import AddMenu, NavigationMenu


def check_object_permission(obj, permission):
    if permission == 'zope.Public':
        permission = CheckerPublic
    return checkPermission(permission, obj)


@menuentry(NavigationMenu)
class LehrheftListing(uvclight.TablePage):
    uvclight.implements(IListing)
    uvclight.context(IFernlehrgang)
    uvclight.name('lehrheft_listing')
    uvclight.title(u'Lehrhefte verwalten')
    uvclight.layer(IFernlehrgangSkin)
    
    template = uvclight.get_template('base_listing.cpt', __file__)

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
            model_lookup.patterns.locate(root, x, DefaultModel)
            yield x


@menuentry(AddMenu)
class AddLehrheft(uvclight.AddForm):
    uvclight.context(IFernlehrgang)
    uvclight.title(u'Lehrheft')
    uvclight.layer(IFernlehrgangSkin)
    
    title = u'Lehrheft'
    label = u'Lehrhefte'
    description = u'Hier können Sie die Lehrhefte für den Fernlehrgang anlegen.'
    fields = uvclight.Fields(ILehrheft).omit('id')

    def create(self, data):
        return Lehrheft(**data)

    def add(self, object):
        self.object = object
        self.context.lehrhefte.append(object)

    def nextURL(self):
        self.flash(u'Das Lehrheft wurde erfolgreich angelegt')
        return self.url(self.context, 'lehrheft_listing')


class EmbeddedFrage(uvclight.View):
    uvclight.context(IFrage)
    uvclight.name('embedded')
    uvclight.layer(IFernlehrgangSkin)

    image = None
    thumb = None

    template = uvclight.get_template("embeddedfrage.cpt", __file__)
    
    def __init__(self, context, request):
        root = uvclight.getSite()
        model_lookup.patterns.locate(root, context, DefaultModel)
        View.__init__(self, context, request)

    def update(self):
        self.id = str(self.context.id)
        self.link = self.url(self.context)
        self.editable = check_object_permission(
            self.context, 'dolmen.content.Edit')
        if self.context.bilder.count():
            self.image = self.context.bild.locate()
            self.thumb = self.context.thumbnail.locate()
  

class LehrheftIndex(uvclight.Page):
    uvclight.context(ILehrheft)
    uvclight.name('index')
    uvclight.layer(IFernlehrgangSkin)

    template = uvclight.get_template('lehrheftindex.cpt', __file__)
    
    def update(self):
        self._fragen = (EmbeddedFrage(frage, self.request)
                        for frage in self.context.fragen)

    @property
    def fragen(self):
        for frage in self._fragen:
            frage.update()
            yield frage.render()


class Edit(uvclight.EditForm):
    uvclight.context(ILehrheft)
    uvclight.title(u'Edit')
    uvclight.name('edit')
    uvclight.layer(IFernlehrgangSkin)

    label = u"Bearbeiten"
    fields = uvclight.Fields(ILehrheft).omit('id')
    
    @property
    def description(self):
        return (u"Hier können Sie das '%s' vom Fernlehrgang "
                u"'%s' bearbeiten." % (self.context.titel, 'MUSS'))


## Spalten

class Id(uvclight.GetAttrColumn):
    uvclight.name('id')
    uvclight.context(IFernlehrgang)
    weight = 5 
    attrName = "id"
    header = "Id"


class Nummer(uvclight.GetAttrColumn):
    uvclight.name('nummer')
    uvclight.context(IFernlehrgang)
    weight = 10
    attrName = "nummer"
    header = "Nummer"


class Name(uvclight.LinkColumn):
    uvclight.name('Nummer')
    uvclight.context(IFernlehrgang)
    weight = 99
    linkContent = "edit"

    def getLinkContent(self, item):
        return item.titel
