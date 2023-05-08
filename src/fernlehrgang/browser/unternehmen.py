# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang import fmtDate
from fernlehrgang.browser import Display, Form, AddForm, EditForm
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.cusa_result import ICusaResult
from fernlehrgang.models import Unternehmen
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from sqlalchemy import func
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import NO_VALUE
from zeam.form.base import action
from fernlehrgang.viewlets import NavEntry
from fernlehrgang.browser import Page


NO_VALUE = ""


grok.templatedir('templates')



class UNNavItem(NavEntry):
    grok.context(IUnternehmen)
    grok.order(10)

    title = "Unternehmen"
    icon = "fas fa-user-tie"

    def url(self):
        return self.view.url(self.context)


class UNNavItem1(NavEntry):
    grok.context(IUnternehmen)
    grok.name('unnav1')
    grok.order(20)

    title = "Teilnehmer"
    icon = "fas fa-user-tie"

    def url(self):
        return self.view.url(self.context, 'teilnehmer_listing')


class UNavItemCusa(NavEntry):
    grok.context(IUnternehmen)
    grok.name('unnavcusa')
    grok.order(30)

    title = "Cusa Integration"
    icon = "fas fa-user-tie"

    def url(self):
        return self.view.url(self.context, 'cusa')


#@menuentry(NavigationMenu)
class UnternehmenListing(Form):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmen_listing')
    grok.title(u"Unternehmen verwalten")
    grok.order(20)

    fields = Fields(IUnternehmen).select('mnr', 'unternehmensnummer', 'hbst', 'name', 'str', 'plz', 'ort', 'mnr_g_alt')

    label = u"Unternehmen verwalten"
    description = u"Hier können Sie die am Fernlehrgang teilnehmenden Unternehmen verwalten"

    results = []

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    def getResults(self):
        for item in self.results:
            locate(grok.getSite(), item, DefaultModel)
            yield item

    @action(u"Suchen")
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = Session()
        sql = session.query(Unternehmen)
        if data.get('mnr') != NO_VALUE:
            sql = sql.filter(Unternehmen.mnr == data.get('mnr'))
            v = True
        if data.get('unternehmensnummer') != NO_VALUE:
            sql = sql.filter(Unternehmen.unternehmensnummer == data.get('unternehmensnummer').replace(' ', ''))
            v = True
        if data.get('hbst') != NO_VALUE:
            sql = sql.filter(Unternehmen.hbst == data.get('hbst'))
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
        ### FIXME length between (100000000 and 1000000000) instead of --> sql = sql.filter(func.length(Unternehmen.mnr) == 9)
        
        self.results = sql.order_by(Unternehmen.name).all()


#@menuentry(NavigationMenu, order=1)
class Index(Display):
    grok.context(IUnternehmen)
    grok.name('index')
    grok.title('Unternehmen')
    template = ChameleonPageTemplateFile('templates/unternehmen_view.cpt')

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
            person = dict(name = "%s %s" %(teilnehmer.name, teilnehmer.vorname),
                          gebdat = gebdat,
                          lehrgang = [])
            for kurs in teilnehmer.kursteilnehmer:
                if kurs.fernlehrgang:
                    person['lehrgang'].append(kurs.fernlehrgang.titel)
            if not len(person['lehrgang']):
                person['lehrgang'].append(u'Noch für keinen Fernlehrgang registriert.')
            rc.append(person)
        return sorted(rc, key=lambda v: v.get('name'))


#@menuentry(AddMenu)
class AddUnternehmen(AddForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Unternehmen')
    title = u'Unternehmen'
    label = u'Unternehmen anlegen'
    description = u"Unternehmen anlegen"

    fields = Fields(IUnternehmen)

    def create(self, data):
        return Unternehmen(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        return self.url(self.context, 'unternehmen_listing')


class Edit(EditForm):
    grok.context(IUnternehmen)
    grok.implements(IListing)
    template = grok.PageTemplateFile('templates/unternehmen_edit.cpt')


class Cusa(Page):
    grok.context(IUnternehmen)
    template = grok.PageTemplateFile('templates/cusa.cpt')

    def results(self):
        return ICusaResult(self.context).persist()
