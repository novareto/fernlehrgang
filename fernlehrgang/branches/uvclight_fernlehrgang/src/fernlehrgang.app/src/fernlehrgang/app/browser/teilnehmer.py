# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from dolmen.app.layout import models, IDisplayView
from dolmen.forms.base.utils import apply_data_event
from dolmen.forms.crud import i18n as _
from dolmen.menu import menuentry, Entry, menu
from fernlehrgang.models import Teilnehmer, Kursteilnehmer, Fernlehrgang
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.z3ctable import TablePage, Column, GetAttrColumn, LinkColumn
from uvc.layout.interfaces import IExtraInfo
from z3c.saconfig import Session
from zeam.form.base import Fields, action, NO_VALUE
from zeam.form.base.markers import FAILURE

from . import Form, AddForm 
from .widgets import fmtDate
from .resources import register_js
from .skin import IFernlehrgangSkin
from .viewlets import AddMenu, NavigationMenu
from ..interfaces import (
    IListing, IKursteilnehmer, ITeilnehmer, generatePassword, IUnternehmen)


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
    grok.layer(IFernlehrgangSkin)
    
    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Teilnehmer"
    batchSize = 150
    startBatchingAt = 150
    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}

    @property
    def description(self):
        return (u"Hier können Sie die Teilnehmer zum Unternehmen "
                u"'%s %s' verwalten." % (self.context.mnr, self.context.name))

    @property
    def values(self):
        return self.context.teilnehmer


@menuentry(AddMenu)
class AddTeilnehmer(AddForm):
    grok.context(IUnternehmen)
    grok.title(u'Teilnehmer')
    grok.layer(IFernlehrgangSkin)
    
    label = u'Teilnehmer anlegen für Unternehmen'
    fields = Fields(ITeilnehmer).omit('id')
    fields['kompetenzzentrum'].mode = "radio"

    def updateForm(self):
        super(AddTeilnehmer, self).updateForm()
        self.fields['passwort'].defaultValue = generatePassword()

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
        session.flush()
        #if kursteilnehmer:
        #    kursteilnehmer.teilnehmer = teilnehmer
        #    kursteilnehmer.unternehmen = self.context
        #    #if kursteilnehmer.fernlehrgang_id:
        #    print "BBB----->", kursteilnehmer.fernlehrgang_id
        #    fernlehrgang = session.query(Fernlehrgang).filter( Fernlehrgang.id == kursteilnehmer.fernlehrgang_id).one()
        #    fernlehrgang.kursteilnehmer.append(kursteilnehmer)

    def nextURL(self):
        self.flash(u'Der Teilnehmer wurde erfolgreich gespeichert')
        return "%s/teilnehmer/%s" %(self.url(), self.tn.id)


class Index(models.DefaultView):
    grok.context(ITeilnehmer)
    grok.layer(IFernlehrgangSkin)
    
    title = label = u"Teilnehmer"
    description = u"Details zu Ihrem Unternehmen"
    __name__ = "index"

    fields = Fields(ITeilnehmer).omit(id, 'lehrgang')


class Edit(models.Edit):
    grok.context(ITeilnehmer)
    grok.layer(IFernlehrgangSkin)
    
    grok.name('edit')
    label = u"Teilnehmer"

    fields = Fields(ITeilnehmer).omit('id')
    fields['kompetenzzentrum'].mode = "radio"

    @action('Speichern')
    def handle_edit(self):
        data, errors = self.extractData()
        if errors:
            self.submissionError = errors
            return FAILURE
        for x in ['adresszusatz', 'ort', 'plz', 'nr',
                  'email', 'strasse', 'telefon']:
            if data[x] == NO_VALUE:
                data[x] = ""
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
    grok.layer(IFernlehrgangSkin)
    grok.title('Registrierung')

    label = u"Teilnehmer für Lehrgang registrieren"
    __name__ = "register"

    fields = Fields(IKursteilnehmer).omit('id', 'teilnehmer_id')

    def update(self):
        register_js.need()

    @action('Registrieren')
    def handle_register(self):
        data, errors = self.extractData()
        if errors:
            return FAILURE
        if data.get('lehrgang') is not NO_VALUE:
            session = Session()
            kursteilnehmer = Kursteilnehmer(
                fernlehrgang_id=data.get('fernlehrgang_id'),
                status=data.get('status'),
                un_klasse = data.get('un_klasse'),
                branche = data.get('branche'),
                unternehmen_mnr=self.context.unternehmen.mnr)
            kursteilnehmer.teilnehmer = self.context
            fernlehrgang = session.query(Fernlehrgang).filter( Fernlehrgang.id == kursteilnehmer.fernlehrgang_id).one()
            print "ADD Kursteilnehmer to Fernlehrgang"
            fernlehrgang.kursteilnehmer.append(kursteilnehmer)
            self.flash('Der Teilnehmer wurde als Kursteilnehmer mit der ID %s angelegt.' % kursteilnehmer.id )
        else:
            self.flash('Es wurde kein Lehrgang spezifiziert.', type="warning")
        self.redirect(self.url(self.context))

    @action(u'Registrierung ändern', identifier='reg-change')
    def handle_update(self):
        data, errors = self.extractData()
        if errors:
            return FAILURE
        session = Session()
        from fernlehrgang.models import Kursteilnehmer
        ktn_id, flg_id = data.get('fernlehrgang_id').split(',')
        ktn = session.query(Kursteilnehmer).get(ktn_id)
        ktn.status = data.get('status')
        ktn.branche = data.get('branche')
        ktn.gespraech = data.get('gespraech')
        ktn.un_klasse = data.get('un_klasse')
        session.flush()


class TeilnehmerJSONViews(grok.JSON):
    grok.context(ITeilnehmer)

    def get_kursteilnehmer(self, ktn_id):
        session = Session()
        from fernlehrgang.models import Kursteilnehmer
        ktn_id, flg_id = ktn_id.split(',')
        ktn = session.query(Kursteilnehmer).get(ktn_id)
        print {'status': ktn.status, 'un_klasse': ktn.un_klasse, 'branche': ktn.branche, 'gespraech': ktn.gespraech}
        return {'status': ktn.status, 'un_klasse': ktn.un_klasse, 'branche': ktn.branche, 'gespraech': ktn.gespraech}


class OverviewKurse(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(ITeilnehmer)
    grok.layer(IFernlehrgangSkin)
    grok.order(30)

    def update(self):
        session = Session()
        sql = session.query(Kursteilnehmer).filter(Kursteilnehmer.teilnehmer_id == self.context.id)
        self.res = sql.all()


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
            return fmtDate(item.geburtsdatum)
        return ""
