# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.app.layout import models, IDisplayView
from dolmen.forms.base.utils import set_fields_data, apply_data_event
from dolmen.forms.crud import i18n as _
from dolmen.menu import menuentry, Entry, menu
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.models import Teilnehmer, Kursteilnehmer, Fernlehrgang
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import TablePage, Column, GetAttrColumn, LinkColumn
from profilestats import profile
from uvc.layout.interfaces import IExtraInfo
from uvc.layout.zeamform import Form 
from z3c.saconfig import Session
from zeam.form.base import Fields, NO_VALUE, action
from zeam.form.base import NO_VALUE, DictDataManager
from zeam.form.base.markers import SUCCESS, FAILURE
from fernlehrgang.interfaces.teilnehmer import generatePassword
from zope.interface import Interface
from zope.component import getMultiAdapter


grok.templatedir('templates')


def no_value(d):
    for key, value in d.items():
        if value is NO_VALUE:
            d[key] = None
    return d


@menuentry(NavigationMenu)
class TeilnehmerListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(IUnternehmen)
    grok.name('teilnehmer_listing')
    grok.title(u'Teilnehmer verwalten')

    template = grok.PageTemplateFile('templates/base_listing.pt')

    label = u"Teilnehmer"
    cssClasses = {'table': 'tablesorter myTable'}

    @property
    def description(self):
        return u"Hier können Sie die Teilnehmer zum Unternehmen '%s %s' verwalten." % (self.context.mnr, self.context.name)

    @property
    def values(self):
        return self.context.teilnehmer


@menuentry(AddMenu)
class AddTeilnehmer(uvc.layout.AddForm):
    grok.context(IUnternehmen)
    grok.title(u'Teilnehmer')
    label = u'Teilnehmer anlegen für Unternehmen'

    fields = Fields(ITeilnehmer).omit('id')

    def create(self, data):
        data = no_value(data)
        #lehrgang = data.pop('lehrgang')
        lehrgang = None
        kursteilnehmer = None
        if lehrgang:
            kursteilnehmer = Kursteilnehmer(
                fernlehrgang_id=lehrgang,
                status="A1", 
                unternehmen_mnr=self.context.mnr)
        teilnehmer = Teilnehmer(**data)
        return (kursteilnehmer, teilnehmer)

    def add(self, object):
        kursteilnehmer, teilnehmer = object
        session = Session()
        self.context.teilnehmer.append(teilnehmer)
        self.tn = teilnehmer
        #if kursteilnehmer:
        #    kursteilnehmer.teilnehmer = teilnehmer
        #    kursteilnehmer.unternehmen = self.context
        #    #if kursteilnehmer.fernlehrgang_id:
        #    print "BBB----->", kursteilnehmer.fernlehrgang_id
        #    fernlehrgang = session.query(Fernlehrgang).filter( Fernlehrgang.id == kursteilnehmer.fernlehrgang_id).one()
        #    fernlehrgang.kursteilnehmer.append(kursteilnehmer)

    def nextURL(self):
        self.flash(u'Der Teilnehmer wurde erfolgreich gespeichert')
        locate(grok.getSite(), self.tn, DefaultModel)
        return self.url(self.tn)


class Index(models.DefaultView):
    grok.context(ITeilnehmer)
    title = label = u"Teilnehmer"
    description = u"Details zu Ihrem Unternehmen"
    __name__ = "index"

    fields = Fields(ITeilnehmer).omit(id, 'lehrgang')


class Edit(models.Edit):
    grok.context(ITeilnehmer)
    grok.name('edit')
    label = u"Teilnehmer"

    fields = Fields(ITeilnehmer).omit('id')

    @action('Speichern')
    def handle_edit(self):
        data, errors = self.extractData()
        if errors:
            self.submissionError = errors
            return FAILURE

        #lehrgang = data.pop('lehrgang')
        #if lehrgang is not NO_VALUE:
        #    session = Session()
        #    kursteilnehmer = Kursteilnehmer(
        #        fernlehrgang_id=lehrgang,
        #        status="A1", 
        #        unternehmen_mnr=self.context.unternehmen.mnr)
        #    kursteilnehmer.teilnehmer = self.context
        #    fernlehrgang = session.query(Fernlehrgang).filter( Fernlehrgang.id == kursteilnehmer.fernlehrgang_id).one()
        #    print "ADD Kursteilnehmer to Fernlehrgang"
        #    fernlehrgang.kursteilnehmer.append(kursteilnehmer)
            
        apply_data_event(self.fields, self.getContentData(), data)
        self.flash(_(u"Content updated"))
        self.redirect(self.url(self.context))

    
    @action('Abbrechen')
    def handle_cancel(self):
        self.flash(u'Ihre Aktion wurde abgebrochen.')
        self.redirect(self.url(self.context))


@menuentry(NavigationMenu, order=200)
class Register(Form):
    grok.context(ITeilnehmer)
    grok.name('register')
    grok.title('Registrierung')
    label = u"Teilnehmer für Lehrgang registrieren"
    __name__ = "register"

    fields = Fields(IKursteilnehmer).omit('id', 'teilnehmer_id')

    @action('Registrieren')
    def handle_register(self):
        data, errors = self.extractData()
        if errors:
            return FAILURE
        if data.get('lehrgang') is not NO_VALUE:
            session = Session()
            kursteilnehmer = Kursteilnehmer(
                fernlehrgang_id=data.get('lehrgang'),
                status=data.get('status'),
                un_klasse = data.get('un_klasse'),
                branche = data.get('branche'),
                unternehmen_mnr=self.context.unternehmen.mnr)
            kursteilnehmer.teilnehmer = self.context
            fernlehrgang = session.query(Fernlehrgang).filter( Fernlehrgang.id == kursteilnehmer.fernlehrgang_id).one()
            print "ADD Kursteilnehmer to Fernlehrgang"
            fernlehrgang.kursteilnehmer.append(kursteilnehmer)
        self.flash('Der Teilnehmer wurde als Kursteilnehmer mit der ID %s angelegt.' % kursteilnehmer.id )


# More Info Viewlets

class MoreInfoUnternehmen(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IUnternehmen) 
    grok.order(10)

    def render(self):
        return "<h3>Mitgliedsnummer: %s, Unternehmen: %s </h3>" %(self.context.mnr, self.context.name)


class MoreInfoOnTeilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(ITeilnehmer)
    grok.order(10)

    def render(self):
        return "<h3>Mitgliedsnummer: %s, Unternehmen: %s </h3>" %(self.context.unternehmen.mnr, self.context.unternehmen.name)


class OverviewKurse(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(ITeilnehmer)
    grok.order(30)

    def update(self):
        session = Session()
        sql = session.query(Kursteilnehmer).filter(Kursteilnehmer.teilnehmer_id == self.context.id)
        self.res = sql.all()


class DisplayTeilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(ITeilnehmer)
    grok.view(Register)
    grok.order(20)

    def update(self):
        self.view = getMultiAdapter((self.context, self.request), Interface, name="index")
        self.view.update()
        self.view.updateWidgets()



class HelperEntry(Entry):
    grok.name('index')
    grok.context(ITeilnehmer)
    grok.order(1)
    grok.title('Teilnehmer')
    menu(NavigationMenu)


## Spalten

class ID(GetAttrColumn):
    grok.name('Id')
    grok.context(IUnternehmen)
    weight = 5 
    header = u"Id"
    attrName = "id"


class Name(LinkColumn):
    grok.name('Name')
    grok.context(IUnternehmen)
    weight = 10 
    linkContent = "edit"

    def getLinkURL(self, item):
        return self.table.url().replace('_listing', '/'+str(item.id))

    def getLinkContent(self, item):
        return item.name


class VorName(GetAttrColumn):
    grok.name('VorName')
    grok.context(IUnternehmen)
    weight = 20
    header = u"Vorname"
    attrName = "vorname"


class Geburtsdatum(Column):
    grok.name('Geburtsdatum')
    grok.context(IUnternehmen)
    weight = 30
    header = u"Geburtsdatum"

    def renderCell(self, item):
        if item.geburtsdatum != None:
            return item.geburtsdatum.strftime('%d.%m.%Y')
        return ""
