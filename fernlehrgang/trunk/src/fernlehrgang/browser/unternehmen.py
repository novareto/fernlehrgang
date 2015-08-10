# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.app.layout import models
from dolmen.menu import menuentry
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import Unternehmen
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import NO_VALUE
from zeam.form.base import action
from grokcore.chameleon.components import ChameleonPageTemplateFile
from fernlehrgang import Form, AddForm, fmtDate
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from sqlalchemy import func


NO_VALUE = ""


grok.templatedir('templates')


@menuentry(NavigationMenu)
class UnternehmenListing(Form):
    grok.context(IFernlehrgangApp)
    grok.name('unternehmen_listing')
    grok.title(u"Unternehmen verwalten")
    grok.order(20)

    fields = Fields(IUnternehmen).select('mnr', 'name', 'str', 'plz', 'ort', 'mnr_g_alt')

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


class Index(models.DefaultView):
    grok.context(IUnternehmen)
    grok.name('index')
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
                print kurs.fernlehrgang
                if kurs.fernlehrgang:
                    person['lehrgang'].append(kurs.fernlehrgang.titel)
            if not len(person['lehrgang']):
                person['lehrgang'].append(u'Noch für keinen Fernlehrgang registriert.')
            rc.append(person)
        return rc


@menuentry(AddMenu)
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


class Edit(models.Edit):
    grok.context(IUnternehmen)
    grok.implements(IListing)
    template = grok.PageTemplateFile('templates/unternehmen_edit.cpt')
