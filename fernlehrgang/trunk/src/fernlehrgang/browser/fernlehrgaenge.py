# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import GetAttrColumn, LinkColumn
from uvc.layout import TablePage
from z3c.saconfig import Session
from zeam.form.base import Fields
from grokcore.chameleon.components import ChameleonPageTemplateFile
from fernlehrgang import AddForm

grok.templatedir('templates')


@menuentry(NavigationMenu)
class FernlehrgangListing(TablePage):
    grok.implements(IDisplayView)
    grok.context(IFernlehrgangApp)
    grok.name('fernlehrgang_listing')
    grok.title(u"Fernlehrgänge")
    grok.order(10)

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Fernlehrgänge"
    description = u"Hier können Sie die Fernlehrgänge der BG verwalten."

    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}
    status = None

    @property
    def values(self):
        root = grok.getSite()
        session = Session()
        for fernlehrgang in session.query(Fernlehrgang).all():
            locate(root, fernlehrgang, DefaultModel)
            yield fernlehrgang


@menuentry(AddMenu)
class AddFernlehrgang(AddForm):
    grok.implements(IDisplayView)
    grok.context(IFernlehrgangApp)
    grok.title(u'Fernlehrgang')
    title = u'Fernlehrgang'
    label = u'Fernlehrgang anlegen'
    description = u""

    fields = Fields(IFernlehrgang).omit('id')

    def create(self, data):
        return Fernlehrgang(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        self.flash(u'Der Fernlehrgang wurde erfolgreich angelegt.')
        url = self.url(self.context)
        return url


class Index(models.DefaultView):
    grok.context(IFernlehrgang)
    fields = Fields(IFernlehrgang).omit('id')

    @property
    def label(self):
        return u"Fernlehrgang: %s (%s)" % (
            self.context.titel, self.context.id)


class Edit(models.Edit):
    grok.context(IFernlehrgang)
    label = u"Fernlehrgang bearbeiten"
    description = u"Hier können Sie Ihren Fernlehrgang bearbeiten"
    fields = Fields(IFernlehrgang).omit('id')


### Spalten

class ID(GetAttrColumn):
    grok.name('Id')
    grok.context(IFernlehrgangApp)
    weight = 5
    header = u"Id"
    attrName = u"id"

class Title(LinkColumn):
    grok.name('titel')
    grok.context(IFernlehrgangApp)
    weight = 10
    header = u"Titel"
    attrName = u"titel"

    def getLinkContent(self, item):
        return item.titel


class Jahr(GetAttrColumn):
    grok.name('Jahr')
    grok.context(IFernlehrgangApp)
    weight = 20
    header = u"Jahr"
    attrName = u"jahr"
