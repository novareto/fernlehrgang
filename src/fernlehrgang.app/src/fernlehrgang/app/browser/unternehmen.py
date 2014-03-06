# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import uvclight
from uvclight.backends.patterns import DefaultModel

from dolmen.forms.base import Fields, NO_VALUE, action
from dolmen.menu import menuentry
from fernlehrgang.models import Unternehmen 
from sqlalchemy import func
from cromlech.sqlalchemy import get_session
from zope.location import locate

from . import Form, AddForm, EditForm, DefaultView
from ..interfaces import IListing, IFernlehrgangApp, IUnternehmen
from ..wsgi import IFernlehrgangSkin, model_lookup
from .viewlets import AddMenu, NavigationMenu
from .widgets import fmtDate

NO_VALUE = ''


@menuentry(NavigationMenu)
class UnternehmenListing(uvclight.Form):
    uvclight.context(IFernlehrgangApp)
    uvclight.name('unternehmen_listing')
    uvclight.title(u"Unternehmen verwalten")
    uvclight.layer(IFernlehrgangSkin)
    uvclight.order(20)

    template = uvclight.get_template('unternehmenlisting.cpt', __file__)
    
    fields = Fields(IUnternehmen).select(
        'mnr', 'name', 'str', 'plz', 'ort', 'mnr_g_alt')

    label = u"Unternehmen verwalten"
    description = (u"Hier können Sie die am Fernlehrgang " +
                   u"teilnehmenden Unternehmen verwalten")

    results = []

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    def getResults(self):
        for item in self.results:
            model_lookup.patterns.locate(uvclight.getSite(), item, DefaultModel)
            yield item

    @action(u"Suchen")
    def handle_search(self): 
        v = False
        data, errors = self.extractData()
        session = get_session('fernlehrgang')
        sql = session.query(Unternehmen)
        if data.get('mnr') != NO_VALUE:
            sql = sql.filter(Unternehmen.mnr == data.get('mnr'))
            v = True
        if data.get('mnr_g_alt') != NO_VALUE:
            sql = sql.filter(Unternehmen.mnr_g_alt == data.get('mnr_g_alt'))
            v = True
        if data.get('name') != NO_VALUE:
            constraint = "%%%s%%" % data.get('name')
            sql = sql.filter(Unternehmen.name.ilike(constraint))
            v = True
        if data.get('str') != NO_VALUE:
            constraint = "%%%s%%" % data.get('str')
            sql = sql.filter(Unternehmen.str.ilike(constraint))
            v = True
        if data.get('plz') != NO_VALUE:
            sql = sql.filter(Unternehmen.plz == data.get('plz'))
            v = True
        if data.get('ort') != NO_VALUE:
            constraint = "%%%s%%" % data.get('ort')
            sql = sql.filter(Unternehmen.ort.ilike(constraint))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie die Suchkriterien ein.')
            return
        sql = sql.filter(func.length(Unternehmen.mnr) == 9)
        self.results = sql.all()


class Index(DefaultView):
    uvclight.context(IUnternehmen)
    uvclight.name('index')
    uvclight.layer(IFernlehrgangSkin)

    template = uvclight.get_template('unternehmen_view.cpt', __file__)

    title = u"Unternehmen"
    label = u"Unternehmen"
    description = u"Details zum Unternehmen"

    fields = Fields(IUnternehmen)

    def getTeilnehmerListing(self):
        rc = []
        for teilnehmer in self.context.teilnehmer:
            gebdat = ""
            if teilnehmer.geburtsdatum:
                gebdat = fmtDate(teilnehmer.geburtsdatum)
            person = dict(
                name="%s %s" %(teilnehmer.name, teilnehmer.vorname),
                gebdat=gebdat,
                lehrgang=[])
            for kurs in teilnehmer.kursteilnehmer:
                print kurs.fernlehrgang
                if kurs.fernlehrgang:
                    person['lehrgang'].append(kurs.fernlehrgang.titel)
            if not len(person['lehrgang']):
                person['lehrgang'].append(
                    u'Noch für keinen Fernlehrgang registriert.')
            rc.append(person)
        return rc


from dolmen.location import get_absolute_url

@menuentry(AddMenu) 		
class AddUnternehmen(AddForm): 		
    uvclight.context(IFernlehrgangApp) 		
    uvclight.title(u'Unternehmen')
    uvclight.layer(IFernlehrgangSkin)

    title = u'Unternehmen' 		
    label = u'Unternehmen anlegen' 		
    description = u"Unternehmen anlegen" 		

    fields = Fields(IUnternehmen) 		

    def create(self, data): 		
        return Unternehmen(**data) 		

    def add(self, object): 		
        session = get_session('fernlehrgang') 		
        session.add(object)

    def nextURL(self): 		
        return get_absolute_url(self.context, self.request) + 'unternehmen_listing'
        return self.url(self.context, 'unternehmen_listing')


class Edit(EditForm):
    uvclight.context(IUnternehmen)
    uvclight.implements(IListing)
    uvclight.layer(IFernlehrgangSkin)

    template = 'templates/unternehmen_edit.cpt'
