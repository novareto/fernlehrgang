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
from ..wsgi import model_lookup
from fernlehrgang.models import lieferstopps, Teilnehmer, Kursteilnehmer
from cromlech.sqlalchemy import get_session


_ = MessageFactory('dolmen.forms.base')


@menuentry(NavigationMenu)
class KursteilnehmerListing(uvclight.Form):
    uvclight.context(IFernlehrgang)
    uvclight.name('kursteilnehmer_listing')
    uvclight.title("Kursteilnehmer verwalten")
    uvclight.order(10)

    template = uvclight.get_template('kursteilnehmerlisting.cpt', __file__)

    fields = uvclight.Fields(ITeilnehmer).select('id', 'name', 'geburtsdatum')

    label = u"Kursteilnehmer"
    description = (u"Hier können Sie die Kursteilnehmer für "
                   u"Ihren Fernlehrgang suchen und bearbeiten.")

    results = []

    def getResults(self):
        root = uvclight.getSite()
        lf_vocab = lieferstopps(None)
        for teilnehmer, kursteilnehmer in self.results:
            model_lookup.patterns.locate(root, kursteilnehmer, DefaultModel)
            model_lookup.patterns.locate(root, teilnehmer.unternehmen, DefaultModel)
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
        session = get_session('fernlehrgang')
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
        if data.get('geburtsdatum'):
            sql = sql.filter(Teilnehmer.geburtsdatum ==
                             data.get('geburtsdatum'))
            v = True
        if not v:
            self.flash(u'Bitte geben Sie Suchkriterien ein.')
            return
        self.results = sql.all()



@menuentry(AddMenu)
class AddKursteilnehmer(uvclight.Form):
    uvclight.context(IFernlehrgang)
    uvclight.title(u'Kursteilnehmer')
    label = u'Kursteilnehmer anlegen'
    description = u'Kursteilnehmer anlegen'

    fields = uvclight.Fields(IKursteilnehmer).select('teilnehmer_id')

    @uvclight.action(u'Suchen und Registrieren')
    def handleSearch(self):
        data, errors = self.extractData()
        if errors:
            return
        session = get_session('fernlehrgang')
        sql = session.query(Teilnehmer).filter(
            Teilnehmer.id == data.get('teilnehmer_id'))
        if sql.count() == 0:
            self.flash('Es wurde kein Teilnehmer mit der ID %s gefunden' %
                       data.get('teilnehmer_id'))
        teilnehmer = sql.one()
        model_lookup.patterns.locate(uvclight.getSite(), teilnehmer, DefaultModel)
        self.redirect(self.url(teilnehmer, 'register'))


class Index(uvclight.DefaultView):
    uvclight.context(IKursteilnehmer)
    uvclight.title(u'View')
    title = label = u"Kursteilnehmer"
    description = u"Details zum Kursteilnehmer"

    fields = uvclight.Fields(IKursteilnehmer).omit(id)


class Edit(uvclight.EditForm):
    uvclight.context(IKursteilnehmer)
    uvclight.name('edit')
    uvclight.title(u'Edit')

    fields = uvclight.Fields(IKursteilnehmer).omit('id')
    fields['teilnehmer_id'].mode = 'hiddendisplay'
    fields['fernlehrgang_id'].mode = 'hiddendisplay'
    fields['branche'].mode = "radio"


class MoreInfoOnKursteilnehmer(uvclight.Viewlet):
    uvclight.viewletmanager(IExtraInfo)
    uvclight.context(IKursteilnehmer)
    template = uvclight.get_template('moreinfoonkursteilnehmer.cpt',  __file__)

    def update(self):
        url = uvclight.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url
        model_lookup.patterns.locate(uvclight.getSite(), self.context.teilnehmer, DefaultModel)
        self.turl = '<a href="%s/edit"> %s %s </a>' %(
                self.view.url(self.context.teilnehmer),
                self.context.teilnehmer.name, self.context.teilnehmer.vorname)
