# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grok import url, getSite
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from uvc.layout.interfaces import ISidebar
from fernlehrgang.models import Fernlehrgang
from megrok.traject.components import DefaultModel
from fernlehrgang.ui_components import AddMenu, NavigationMenu
from fernlehrgang.interfaces.flg import IFernlehrgang
from megrok.z3cform.tabular import DeleteFormTablePage
from fernlehrgang.interfaces.app import IFernlehrgangApp

from dolmen.app.layout import ContextualMenuEntry
from dolmen.app.layout import models
from megrok.z3ctable import CheckBoxColumn, LinkColumn, GetAttrColumn 
from megrok.z3cform.base import PageEditForm, PageDisplayForm, PageAddForm, Fields, button, extends
from megrok.z3cform.base.directives import cancellable 
from uvc.widgets import DatePickerCSS, DatePicker


grok.templatedir('templates')


@menuentry(NavigationMenu)
class FernlehrgangListing(DeleteFormTablePage):
    grok.context(IFernlehrgangApp)
    grok.name('fernlehrgang_listing')
    grok.title(u"Fernlehrgänge")
    grok.require('uvc.managefernlehrgang')
    grok.order(10)
    extends(DeleteFormTablePage)
    
    template = grok.PageTemplateFile('templates/base_listing.pt')

    title = u"Fernlehrgänge"
    description = u"Hier können Sie die Fernlehrgaenge der BG-Verwalten"

    cssClasses = {'table': 'tablesorter myTable'}
    status = None

    @property
    def values(self):
        root = getSite()
        session = Session()
        for fernlehrgang in session.query(Fernlehrgang).all():
            locate(root, fernlehrgang, DefaultModel)
            yield fernlehrgang 

    def executeDelete(self, item):
        session = Session()
        session.delete(item)
        self.flash(u'Der Fernlehrgang wurde erfolgreich gelöscht.')
        self.nextURL = self.url(self.context, 'fernlehrgang_listing')
        self.request.response.redirect(self.nextURL)

    def render(self):
        if self.nextURL is not None:
            self.flash(u'Die Objecte wurden gelöscht')
            self.request.response.redirect(self.nextURL)
            return ""
        return self.renderFormTable()
    render.base_method = True    

    @button.buttonAndHandler(u'Fernlehrgang anlegen')
    def handleAddUnternehmen(self, action):
         self.redirect(self.url(self.context, 'addfernlehrgang')) 


@menuentry(AddMenu)
class AddFernlehrgang(PageAddForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Fernlehrgang')
    title = u'Fernlehrgang'
    label = u'Fernlehrgang anlegen'
    description = u""
    cancellable(True)

    fields = Fields(IFernlehrgang).omit('id')

    def updateWidgets(self):
        super(AddFernlehrgang, self).updateWidgets()
        DatePickerCSS.need()
        DatePicker.need()
        self.widgets['beginn'].klass = "datepicker"
        self.widgets['ende'].klass = "datepicker"

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
    extends(PageEditForm)
    fields = Fields(IFernlehrgang).omit('id')

    @button.buttonAndHandler(u'Fernlehrgang entfernen')
    def handleDeleteFernlehrgang(self, action):
        session = Session()
        session.delete(self.context)
        self.flash(u'Der Fernlehrgang wurde erfolgreich gelöscht.')
        self.redirect(self.url(self.context.__parent__)) 

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        DatePickerCSS.need()
        DatePicker.need()
        self.widgets['beginn'].klass = "datepicker"
        self.widgets['ende'].klass = "datepicker"

### Spalten

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.context(IFernlehrgangApp)
    weight = 0
    cssClasses = {'th': 'checkBox'}


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

