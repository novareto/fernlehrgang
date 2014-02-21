# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import time
import json
from datetime import date, datetime, timedelta
import uvclight

from dolmen.menu import menuentry
from fernlehrgang.models import Fernlehrgang
from grokcore.chameleon.components import ChameleonPageTemplateFile
from uvclight import Page
from zope.location import LocationProxy, locate
from megrok.z3ctable import TablePage, GetAttrColumn, LinkColumn
from dolmen.forms.base import Fields

from . import AddForm, DefaultView, EditForm, pagetemplate
from ..interfaces import IFernlehrgang, IFernlehrgangApp
from ..wsgi import IFernlehrgangSkin
from .resources import bs_calendar
from .viewlets import AddMenu, NavigationMenu


@menuentry(NavigationMenu, order=-1)
class FernlehrgangListing(TablePage):
    uvclight.context(IFernlehrgangApp)
    uvclight.name('fernlehrgang_listing')
    uvclight.title(u"Fernlehrgänge")
    uvclight.order(10)
    uvclight.layer(IFernlehrgangSkin)

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Fernlehrgänge"
    description = u"Hier können Sie die Fernlehrgänge der BG verwalten."

    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}
    status = None

    @property
    def values(self):
        root = uvclight.getSite()
        session = Session()
        for fernlehrgang in session.query(Fernlehrgang).all():
            locate(root, fernlehrgang, DefaultModel)
            yield fernlehrgang


@menuentry(AddMenu)
class AddFernlehrgang(AddForm):
    uvclight.name('add-Fernlehrgang')
    uvclight.context(IFernlehrgangApp)
    uvclight.title(u'Fernlehrgang')
    uvclight.layer(IFernlehrgangSkin)
    
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


class SessionsFeeder(uvclight.View):
    uvclight.context(IFernlehrgang)

    @staticmethod
    def timestamp(d):
        return time.mktime(d.timetuple())*1e3 + d.microsecond/1e3

    @property
    def sessions(self):
        for lesson in self.context.lehrhefte:
            lesson = LocationProxy(lesson)
            locate(lesson, self.context, lesson.id)
            session = datetime.combine(lesson.vdatum, datetime.min.time())
            date_start = datetime.combine(session, datetime.min.time())
            date_end = date_start + timedelta(hours=23, minutes=59)
            ts_start = self.timestamp(date_start)
            ts_end = self.timestamp(date_end)
            yield {
                "id": lesson.id,
                "title": lesson.titel,
                "url": 'lehrheft/%s' % lesson.id,
                "class": "event-important",
                "start": ts_start,
                "end": ts_end,
                }
            
        
    def render(self):
        result = {
            "success": 1,
            "result": list(self.sessions),
            }
        self.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        return json.dumps(result)


@menuentry(NavigationMenu, order=60)
class Sessions(Page):
    uvclight.title('Terminliste')
    uvclight.context(IFernlehrgang)
    uvclight.layer(IFernlehrgangSkin)

    def update(self):
        bs_calendar.need()

    
@menuentry(NavigationMenu, order=-2)
class FernlehrgangIndex(DefaultView):
    uvclight.context(IFernlehrgang)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.title('Index')
    uvclight.name('index')
    
    fields = Fields(IFernlehrgang).omit('id')
    
    @property
    def label(self):
        return u"Fernlehrgang: %s (%s)" % (
            self.context.titel, self.context.id)


class Edit(EditForm):
    uvclight.context(IFernlehrgang)
    label = u"Fernlehrgang bearbeiten"
    description = u"Hier können Sie Ihren Fernlehrgang bearbeiten"
    fields = Fields(IFernlehrgang).omit('id')


### Spalten
class ID(GetAttrColumn):
    uvclight.name('Id')
    uvclight.context(IFernlehrgangApp)
    weight = 5 
    header = u"Id"
    attrName = u"id"


class Title(LinkColumn):
    uvclight.name('titel')
    uvclight.context(IFernlehrgangApp)
    weight = 10
    header = u"Titel"
    attrName = u"titel"

    def getLinkContent(self, item):
        return item.titel


class Jahr(GetAttrColumn):
    uvclight.name('Jahr')
    uvclight.context(IFernlehrgangApp)
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
