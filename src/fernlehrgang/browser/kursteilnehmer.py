# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer, lieferstopps
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.models import Teilnehmer, Kursteilnehmer
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from sqlalchemy import and_
from uvc.layout.interfaces import IExtraInfo
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import NO_VALUE
from zeam.form.base import action
from zeam.form.base.errors import Error
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('zeam.form.base')

grok.templatedir('templates')


@menuentry(NavigationMenu)
class KursteilnehmerListing(uvc.layout.Form):
    grok.context(IFernlehrgang)
    grok.implements(IDisplayView)
    grok.name('kursteilnehmer_listing')
    grok.title("Kursteilnehmer verwalten")
    grok.order(10)

    fields = Fields(IKursteilnehmer).select('id') + Fields(ITeilnehmer).select('name', 'geburtsdatum')

    label = u"Kursteilnehmer"
    description = u"Hier können Sie die Kursteilnehmer für Ihren Fernlehrgang suchen und bearbeiten."

    results = []

    def getResults(self):
        root = grok.getSite()
        lf_vocab = lieferstopps(None)
        for teilnehmer, kursteilnehmer in self.results:
            locate(root, kursteilnehmer, DefaultModel)
            locate(root, teilnehmer.unternehmen, DefaultModel)
            name = '<a href="%s"> %s %s </a>' %(self.url(kursteilnehmer), teilnehmer.name, teilnehmer.vorname)
            unternehmen = '<a href="%s"> %s %s </a>' %(self.url(teilnehmer.unternehmen), teilnehmer.unternehmen.mnr, teilnehmer.unternehmen.name)
            r = dict(name=name,
                     id = kursteilnehmer.id,
                     status=lf_vocab.getTerm(kursteilnehmer.status).title,
                     unternehmen=unternehmen)
            yield r 

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    @action(u'Suchen')
    def handle_search(self):
        v=False
        data, errors = self.extractData()
        session = Session()
        flg_id = self.context.id
        sql = session.query(Teilnehmer, Kursteilnehmer)
        sql = sql.filter(and_(Kursteilnehmer.fernlehrgang_id == flg_id, Kursteilnehmer.teilnehmer_id == Teilnehmer.id))
        if data.get('id') != NO_VALUE:
            sql = sql.filter(Kursteilnehmer.id == data.get('id'))
            v = True
        if data.get('name') != NO_VALUE:
            qu = "%%%s%%" % data.get('name')
            sql = sql.filter(Teilnehmer.name.ilike(qu))
            v = True
        if data.get('geburtsdatum') != NO_VALUE:
            sql = sql.filter(Teilnehmer.geburtsdatum == data.get('geburtsdatum'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()



@menuentry(AddMenu)
class AddKursteilnehmer(uvc.layout.AddForm):
    grok.context(IFernlehrgang)
    grok.title(u'Kursteilnehmer')
    label = u'Kursteilnehmer anlegen'
    description = u'Kursteilnehmer anlegen'

    fields = Fields(IKursteilnehmer).omit('id')

    def validateData(self, fields, data, errors):
        super(AddKursteilnehmer, self).validateData(fields, data, errors)
        if len(errors) > 0:
            return errors
        session = Session()
        sql = session.query(Kursteilnehmer).filter( and_(
            Kursteilnehmer.teilnehmer_id == data.get('teilnehmer_id'),
            Kursteilnehmer.fernlehrgang_id == self.context.id))
        if sql.count() > 0:
            errors.append(Error(u"Es ist bereits in Kursteilnehmer mit der Id '%s' angelegt." % data.get('teilnehmer_id'), 'teilnehmer_id'))
        teilnehmer = session.query(Teilnehmer).get(data.get('teilnehmer_id'))
        if not teilnehmer:
            errors.append(Error(u"Es ist kein Teilnehmer mit der Id '%s' vorhanden." % data.get('teilnehmer_id'), 'teilnehmer_id'))
        if len(errors):
            errors.append(Error(_(u"There were errors."), self.prefix))
        return errors

    def create(self, data):
        return Kursteilnehmer(**data)

    def add(self, object):
        self.object = object
        self.context.kursteilnehmer.append(object)

    def nextURL(self):
        self.flash(u'Der Kursteilnehmer wurde erfolgreich angemeldet')
        return self.url(self.context, 'kursteilnehmer_listing')



class Index(models.DefaultView):
    grok.context(IKursteilnehmer)
    grok.title(u'View')
    title = label = u"Kursteilnehmer"
    description = u"Details zum Kursteilnehmer"

    fields = Fields(IKursteilnehmer).omit(id)


class Edit(models.Edit):
    grok.context(IKursteilnehmer)
    grok.name('edit')
    grok.title(u'Edit')

    fields = Fields(IKursteilnehmer).omit('id')
    fields['teilnehmer_id'].mode = 'hiddendisplay'

# More Info Viewlets

class MoreInfoKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IFernlehrgang) 

    def render(self):
        return "<h3>Fernlehrgang %s - %s </h3>" % (self.context.jahr, self.context.titel)

class MoreInfoOnKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IKursteilnehmer)
    script = ""

    def update(self):
        url = grok.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url
        locate(grok.getSite(), self.context.teilnehmer, DefaultModel)
        self.turl = '<a href="%s/edit"> %s %s </a>' %(
                self.view.url(self.context.teilnehmer), self.context.teilnehmer.name, self.context.teilnehmer.vorname)

    def render(self):
        return "%s <h3>Fernlehrgang: %s - %s <br> Teilnehmer %s </h3>" % (self.script,
            self.context.fernlehrgang.jahr, self.context.fernlehrgang.titel, self.turl)
