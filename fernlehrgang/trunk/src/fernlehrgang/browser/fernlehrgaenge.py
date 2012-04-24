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
from megrok.z3ctable import TablePage, GetAttrColumn, LinkColumn
from z3c.saconfig import Session
from zeam.form.base import Fields
from grokcore.chameleon.components import ChameleonPageTemplateFile

grok.templatedir('templates')


@menuentry(NavigationMenu)
class FernlehrgangListing(TablePage):
    grok.implements(IDisplayView)
    grok.context(IFernlehrgangApp)
    grok.name('fernlehrgang_listing')
    grok.title(u"Fernlehrgänge")
    #grok.require('uvc.managefernlehrgang')
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
class AddFernlehrgang(uvc.layout.AddForm):
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


#import elementtree.ElementTree as ET
#from elementtree.ElementTree import Element
#class CreateXML(grok.View):
#    grok.context(IFernlehrgang)
#    xml = ""
#
#    def update(self):
#        from elementtree.SimpleXMLWriter import XMLWriter
#        import sys
#        fernlehrgang = self.context

#        w = XMLWriter('/Users/cklinger/Desktop/t.xml')
#        html = w.start("xml")
#        w.start("fernlehrgang")
#        w.element("id", str(fernlehrgang.id))
#        w.element("titel", fernlehrgang.titel)
#        w.element("jahr", str(fernlehrgang.jahr))
#        w.end()
#
#        w.start("kursteilnehmer")
#        for kursteilnehmer in fernlehrgang.kursteilnehmer:
#            w.start("teilnehmer")
#            w.element('id', str(kursteilnehmer.id))
#            w.end()
#        w.end()
#        w.close(html)
#
#    def render(self):
#        return self.xml
