# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import datetime
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
from fernlehrgang import Form, AddForm


_ = MessageFactory('zeam.form.base')

grok.templatedir('templates')


@menuentry(NavigationMenu)
class KursteilnehmerListing(Form):
    grok.context(IFernlehrgang)
    grok.implements(IDisplayView)
    grok.name('kursteilnehmer_listing')
    grok.title("Kursteilnehmer verwalten")
    grok.order(10)

    fields = Fields(ITeilnehmer).select('id', 'name', 'geburtsdatum')

    label = u"Kursteilnehmer"
    description = u"Hier können Sie die Kursteilnehmer für Ihren Fernlehrgang suchen und bearbeiten."

    results = []

    def getResults(self):
        root = grok.getSite()
        lf_vocab = lieferstopps(None)
        for teilnehmer, kursteilnehmer in self.results:
            locate(root, kursteilnehmer, DefaultModel)
            #locate(root, teilnehmer.unternehmen, DefaultModel)
            name = '<a href="%s"> %s %s </a>' %(self.url(kursteilnehmer), teilnehmer.name, teilnehmer.vorname)
            rcu = []
            for unt in teilnehmer.unternehmen:
                locate(root, unt, DefaultModel)
                rcu.append('<a href="%s"> %s %s </a>' %(self.url(unt), unt.mnr, unt.name))
            r = dict(name=name,
                     id = teilnehmer.id,
                     status=lf_vocab.getTerm(kursteilnehmer.status).title,
                     unternehmen=','.join(rcu))
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
        if data.get('id') != "":
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if data.get('name') != "":
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
class AddKursteilnehmer(Form):
    grok.context(IFernlehrgang)
    grok.title(u'Kursteilnehmer')
    label = u'Kursteilnehmer anlegen'
    description = u'Kursteilnehmer anlegen'

    fields = Fields(IKursteilnehmer).select('teilnehmer_id')

    @action(u'Suchen und Registrieren')
    def handleSearch(self):
        data, errors = self.extractData()
        if errors:
            return
        session = Session()
        sql = session.query(Teilnehmer).filter(Teilnehmer.id == data.get('teilnehmer_id'))
        if sql.count() == 0:
            self.flash('Es wurde kein Teilnehmer mit der ID %s gefunden' %data.get('teilnehmer_id'))
        teilnehmer = sql.one()
        locate(grok.getSite(), teilnehmer, DefaultModel)
        self.redirect(self.url(teilnehmer, 'register'))


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
    fields['fernlehrgang_id'].mode = 'hiddendisplay'


@menuentry(NavigationMenu)
class ExtendDate(Form):
    grok.context(IKursteilnehmer)
    grok.title(u'Fristverlängerung')
    grok.name('extend_date')

    title = u"Fristverlängerung"
    description = u"Hier können Sie die Frist für den OFLG neu setzen"

    fields = Fields(IKursteilnehmer).select('erstell_datum')
    fields['erstell_datum'].title = u"Fristverlängerung"
    fields['erstell_datum'].description = u"Fristverlängerung"

    def updateWidgets(self):
        super(ExtendDate, self).updateWidgets()
        dd = self.fieldWidgets.get('form.field.erstell_datum')
        import datetime
        now = datetime.datetime.now() + datetime.timedelta(days=30)
        dd.value = {'form.field.erstell_datum': now.strftime('%d.%m.%Y')}

    @action(u'Frist verlängern')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            return 
        self.context.status = u'A1'
        self.context.erstell_datum = data['erstell_datum'] - datetime.timedelta(days=365)
        self.flash(u'Die Frist für die Fertigstellung des Online-Fernlehrgangs wurde bis zum %s verlängert' % data['erstell_datum'].strftime('%d.%m.%Y'))


class MoreInfoOnKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IKursteilnehmer)

    def update(self):
        url = grok.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url
        locate(grok.getSite(), self.context.teilnehmer, DefaultModel)
        self.turl = '<a href="%s/edit"> %s %s </a>' %(
                self.view.url(self.context.teilnehmer), self.context.teilnehmer.name, self.context.teilnehmer.vorname)
