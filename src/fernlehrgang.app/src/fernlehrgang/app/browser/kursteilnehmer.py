# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry

from megrok.traject import locate
from megrok.traject.components import DefaultModel
from sqlalchemy import and_
from uvc.layout.interfaces import IExtraInfo
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import NO_VALUE
from zeam.form.base import action
from zope.i18nmessageid import MessageFactory

from . import Form
from .viewlets import AddMenu, NavigationMenu
from ..interfaces import IFernlehrgang, ITeilnehmer, IKursteilnehmer
from fernlehrgang.models import Teilnehmer, Kursteilnehmer
from fernlehrgang.models.interfaces import lieferstopps



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
            locate(root, teilnehmer.unternehmen, DefaultModel)
            name = '<a href="%s"> %s %s </a>' %(self.url(kursteilnehmer), teilnehmer.name, teilnehmer.vorname)
            unternehmen = '<a href="%s"> %s %s </a>' %(self.url(teilnehmer.unternehmen), teilnehmer.unternehmen.mnr, teilnehmer.unternehmen.name)
            r = dict(name=name,
                     id = teilnehmer.id,
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
    fields['branche'].mode = "radio"

#    def update(self):
#        super(Edit, self).update()
#        import pdb; pdb.set_trace()                                              


class MoreInfoOnKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IKursteilnehmer)

    def update(self):
        url = grok.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url
        locate(grok.getSite(), self.context.teilnehmer, DefaultModel)
        self.turl = '<a href="%s/edit"> %s %s </a>' %(
                self.view.url(self.context.teilnehmer), self.context.teilnehmer.name, self.context.teilnehmer.vorname)
