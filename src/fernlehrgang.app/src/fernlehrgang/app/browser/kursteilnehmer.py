# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from dolmen.menu import menuentry

from zope.location import locate
from uvclight.backends.patterns import DefaultModel
from sqlalchemy import and_
from uvclight.interfaces import IExtraInfo

from dolmen.forms.base import Fields
from dolmen.forms.base import NO_VALUE
from dolmen.forms.base import action
from zope.i18nmessageid import MessageFactory

from . import Form, DefaultView, EditForm
from .viewlets import AddMenu, NavigationMenu
from ..interfaces import IFernlehrgang, ITeilnehmer, IKursteilnehmer
from fernlehrgang.models import lieferstopps, Teilnehmer, Kursteilnehmer


_ = MessageFactory('dolmen.forms.base')


@menuentry(NavigationMenu)
class KursteilnehmerListing(Form):
    uvclight.context(IFernlehrgang)
    uvclight.name('kursteilnehmer_listing')
    uvclight.title("Kursteilnehmer verwalten")
    uvclight.order(10)

    fields = Fields(ITeilnehmer).select('id', 'name', 'geburtsdatum')

    label = u"Kursteilnehmer"
    description = (u"Hier können Sie die Kursteilnehmer für "
                   u"Ihren Fernlehrgang suchen und bearbeiten.")

    results = []

    def getResults(self):
        root = uvclight.getSite()
        lf_vocab = lieferstopps(None)
        for teilnehmer, kursteilnehmer in self.results:
            locate(root, kursteilnehmer, DefaultModel)
            locate(root, teilnehmer.unternehmen, DefaultModel)
            name = '<a href="%s"> %s %s </a>' % (
                self.url(kursteilnehmer), teilnehmer.name, teilnehmer.vorname)
            unternehmen = '<a href="%s"> %s %s </a>' % (
                self.url(teilnehmer.unternehmen), teilnehmer.unternehmen.mnr,
                teilnehmer.unternehmen.name)
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
        sql = sql.filter(and_(Kursteilnehmer.fernlehrgang_id ==
                              flg_id, Kursteilnehmer.teilnehmer_id ==
                              Teilnehmer.id))
        if data.get('id') != "":
            sql = sql.filter(Teilnehmer.id == data.get('id'))
            v = True
        if data.get('name') != "":
            qu = "%%%s%%" % data.get('name')
            sql = sql.filter(Teilnehmer.name.ilike(qu))
            v = True
        if data.get('geburtsdatum') != NO_VALUE:
            sql = sql.filter(Teilnehmer.geburtsdatum ==
                             data.get('geburtsdatum'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()



@menuentry(AddMenu)
class AddKursteilnehmer(Form):
    uvclight.context(IFernlehrgang)
    uvclight.title(u'Kursteilnehmer')
    label = u'Kursteilnehmer anlegen'
    description = u'Kursteilnehmer anlegen'

    fields = Fields(IKursteilnehmer).select('teilnehmer_id')

    @action(u'Suchen und Registrieren')
    def handleSearch(self):
        data, errors = self.extractData()
        if errors:
            return
        session = Session()
        sql = session.query(Teilnehmer).filter(
            Teilnehmer.id == data.get('teilnehmer_id'))
        if sql.count() == 0:
            self.flash('Es wurde kein Teilnehmer mit der ID %s gefunden' %
                       data.get('teilnehmer_id'))
        teilnehmer = sql.one()
        locate(uvclight.getSite(), teilnehmer, DefaultModel)
        self.redirect(self.url(teilnehmer, 'register'))


class Index(DefaultView):
    uvclight.context(IKursteilnehmer)
    uvclight.title(u'View')
    title = label = u"Kursteilnehmer"
    description = u"Details zum Kursteilnehmer"

    fields = Fields(IKursteilnehmer).omit(id)


class Edit(EditForm):
    uvclight.context(IKursteilnehmer)
    uvclight.name('edit')
    uvclight.title(u'Edit')

    fields = Fields(IKursteilnehmer).omit('id')
    fields['teilnehmer_id'].mode = 'hiddendisplay'
    fields['fernlehrgang_id'].mode = 'hiddendisplay'
    fields['branche'].mode = "radio"


class MoreInfoOnKursteilnehmer(uvclight.Viewlet):
    uvclight.viewletmanager(IExtraInfo)
    uvclight.context(IKursteilnehmer)

    def update(self):
        url = uvclight.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url
        locate(uvclight.getSite(), self.context.teilnehmer, DefaultModel)
        self.turl = '<a href="%s/edit"> %s %s </a>' %(
                self.view.url(self.context.teilnehmer),
                self.context.teilnehmer.name, self.context.teilnehmer.vorname)
