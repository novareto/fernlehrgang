# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import time
import json
from datetime import datetime, timedelta
import uvclight

from dolmen.menu import menuentry
from fernlehrgang.models import Fernlehrgang
from zope.location import LocationProxy

from ..interfaces import IFernlehrgang, IFernlehrgangApp
from ..wsgi import IFernlehrgangSkin, model_lookup
from .resources import bs_calendar
from .viewlets import AddMenu, NavigationMenu
from cromlech.sqlalchemy import get_session
from uvclight.backends.patterns import DefaultModel


@menuentry(NavigationMenu, order=-1)
class FernlehrgangListing(uvclight.TablePage):
    uvclight.context(IFernlehrgangApp)
    uvclight.name('fernlehrgang_listing')
    uvclight.title(u"Fernlehrgänge")
    uvclight.order(10)
    uvclight.layer(IFernlehrgangSkin)

    template = uvclight.get_template('base_listing.cpt', __file__)

    label = u"Fernlehrgänge"
    description = u"Hier können Sie die Fernlehrgänge der BG verwalten."

    cssClasses = {
        'table': 'table table-striped table-bordered table-condensed'}
    status = None

    @property
    def values(self):
        root = uvclight.getSite()
        session = get_session('fernlehrgang')
        for fernlehrgang in session.query(Fernlehrgang).all():
            model_lookup.patterns.locate(root, fernlehrgang, DefaultModel)
            yield fernlehrgang


@menuentry(AddMenu)
class AddFernlehrgang(uvclight.AddForm):
    uvclight.name('add-Fernlehrgang')
    uvclight.context(IFernlehrgangApp)
    uvclight.title(u'Fernlehrgang')
    uvclight.layer(IFernlehrgangSkin)

    title = u'Fernlehrgang'
    label = u'Fernlehrgang anlegen'
    description = u""

    fields = uvclight.Fields(IFernlehrgang).omit('id')

    def create(self, data):
        root = uvclight.getSite()
        flg = Fernlehrgang(**data)
        model_lookup.patterns.locate(root, flg, DefaultModel)
        return flg

    def add(self, obj):
        session = get_session('fernlehrgang')
        session.add(obj)

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
            model_lookup.patterns.locate(lesson, self.context, lesson.id)
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
        self.response.setHeader(
            'Content-Type',
            'application/json; charset=utf-8')
        return json.dumps(result)


@menuentry(NavigationMenu, order=60)
class Sessions(uvclight.Page):
    uvclight.title('Terminliste')
    uvclight.context(IFernlehrgang)
    uvclight.layer(IFernlehrgangSkin)
    template = uvclight.get_template('sessions.cpt', __file__)

    def update(self):
        bs_calendar.need()


@menuentry(NavigationMenu, order=-2)
class FernlehrgangIndex(uvclight.DefaultView):
    uvclight.context(IFernlehrgang)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.title('Index')
    uvclight.name('index')

    fields = uvclight.Fields(IFernlehrgang).omit('id')

    @property
    def label(self):
        return u"Fernlehrgang: %s (%s)" % (
            self.context.titel, self.context.id)


class Edit(uvclight.EditForm):
    uvclight.title(u'Bearbeiten')
    uvclight.context(IFernlehrgang)
    label = u"Fernlehrgang bearbeiten"
    description = u"Hier können Sie Ihren Fernlehrgang bearbeiten"
    fields = uvclight.Fields(IFernlehrgang).omit('id')


### Spalten
class ID(uvclight.GetAttrColumn):
    uvclight.name('Id')
    uvclight.context(IFernlehrgangApp)
    weight = 5
    header = u"Id"
    attrName = u"id"


class Title(uvclight.LinkColumn):
    uvclight.name('titel')
    uvclight.context(IFernlehrgangApp)
    weight = 10
    header = u"Titel"
    attrName = u"titel"

    def getLinkContent(self, item):
        return item.titel


class Jahr(uvclight.GetAttrColumn):
    uvclight.name('Jahr')
    uvclight.context(IFernlehrgangApp)
    weight = 20
    header = u"Jahr"
    attrName = u"jahr"
