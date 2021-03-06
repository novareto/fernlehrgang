# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import os
import uvc.layout

from dolmen.app.layout import models, IDisplayView
from dolmen.forms.base.utils import set_fields_data, apply_data_event
from dolmen.forms.crud import i18n as _
from dolmen.menu import menuentry, Entry, menu
from fernlehrgang import Form, AddForm 
from fernlehrgang import fmtDate
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.search import getTeilnehmerId
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer, generatePassword
from fernlehrgang.interfaces.teilnehmer import generatePassword
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import Unternehmen, Teilnehmer
from fernlehrgang.models import Kursteilnehmer, Fernlehrgang
from fernlehrgang.resources import register_js
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import Column, GetAttrColumn, LinkColumn
from profilestats import profile
from uvc.layout import TablePage
from uvc.layout.interfaces import IExtraInfo
from z3c.saconfig import Session
from zeam.form.base import Fields, NO_VALUE, action
from zeam.form.base import NO_VALUE, DictDataManager
from zeam.form.base.markers import SUCCESS, FAILURE
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema import Set, Choice
from grokcore.component import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from uvc.layout import TablePage
from GenericCache.GenericCache import GenericCache
from fernlehrgang.resources import chosen_js, chosen_css, chosen_ajax
from fernlehrgang.interfaces.kursteilnehmer import un_klasse, janein
from zope.event import notify
from grok import ObjectAddedEvent
from GenericCache import GenericCache
from plone.memoize import ram
from GenericCache.decorators import cached


grok.templatedir('templates')


def no_value(d):
    for key, value in d.items():
        if value is NO_VALUE:
            d[key] = None
    return d


@menuentry(NavigationMenu, order=20)
class TeilnehmerListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(IUnternehmen)
    grok.name('teilnehmer_listing')
    grok.title(u'Teilnehmer verwalten')

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Teilnehmer"
    batchSize = 150
    startBatchingAt = 150
    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}

    @property
    def description(self):
        return u"Hier können Sie die Teilnehmer zum Unternehmen '%s %s' verwalten." % (self.context.mnr, self.context.name)

    @property
    def values(self):
        tns = self.context.teilnehmer
        vv = sorted(tns, key=lambda t: t.name)
        return vv


@menuentry(AddMenu)
class AddTeilnehmer(AddForm):
    grok.context(IUnternehmen)
    grok.title(u'Teilnehmer')
    label = u'Teilnehmer anlegen für Unternehmen'

    fields = Fields(ITeilnehmer).omit('id') + Fields(IKursteilnehmer).select('branche', 'un_klasse')
    fields['kompetenzzentrum'].mode = "radio"

    def updateForm(self):
        super(AddTeilnehmer, self).updateForm()
        self.fields['passwort'].defaultValue = generatePassword()

    def create(self, data):
        data = no_value(data)
        if 'branche' in data.keys():
            self.context.brachne = data.pop('branche')
        if 'un_klasse' in data.keys():
            self.context.un_klasse = data.pop('un_klasse')
        teilnehmer = Teilnehmer(**data)
        teilnehmer.unternehmen_mnr=self.context.mnr
        return teilnehmer

    def add(self, teilnehmer):
        session = Session()
        self.context.teilnehmer.append(teilnehmer)
        self.tn = teilnehmer
        session.flush()
        notify(ObjectAddedEvent(teilnehmer))

    def nextURL(self):
        self.flash(u'Der Teilnehmer wurde erfolgreich gespeichert')
        return "%s/teilnehmer/%s" %(self.url(), self.tn.id)


menuentry(NavigationMenu, order=10)
class Index(models.DefaultView):
    grok.context(ITeilnehmer)
    title = label = u"Teilnehmer"
    description = u"Details zu Ihrem Unternehmen"
    __name__ = "index"

    fields = Fields(ITeilnehmer).omit(id, 'lehrgang')


class SetDefaultMNR(grok.View):
    grok.context(ITeilnehmer)

    def render(self):
        mnr = self.request.get('mnr')
        if mnr:
            self.context.unternehmen_mnr = mnr
        self.redirect(self.application_url())


class Edit(models.Edit):
    grok.context(ITeilnehmer)
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
        for x in ['adresszusatz', 'ort', 'plz', 'nr', 'email', 'strasse', 'telefon']:
            if data[x] == NO_VALUE:
                data[x] = ""
        apply_data_event(self.fields, self.getContentData(), data)
        self.flash(_(u"Content updated"))
        self.redirect(self.url(self.context))

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash(u'Ihre Aktion wurde abgebrochen.')
        self.redirect(self.url(self.context))



def default_marshaller(func, *args, **kwargs):
    """
    Default marshaller
    """
    return repr((func.__name__,))



class MyVoc(SimpleVocabulary):

    def __init__(self):
        self.session = Session()

    def getTerm(self, term):
        mnr = term.mnr
        name = term.name
        return SimpleTerm(mnr, mnr, "%s - %s" % (mnr, name))

    def getTermByToken(self, token):
        unternehmen = self.session.query(Unternehmen).get(token)
        mnr = unternehmen.mnr
        name = unternehmen.name
        return SimpleTerm(mnr, mnr, "%s - %s" % (mnr, name))


@provider(IContextSourceBinder)
def voc_unternehmen(context):
    return MyVoc()

class ICompany(Interface):

    unternehmen = Set(
        title=u"Unternehmen",
        value_type=Choice(source=voc_unternehmen),
        required=True)

    un_klasse = Choice(
        title = u"Mitarbeiteranzahl",
        description = u'Hier können Sie die Gruppe des Unternehmens festlegen.',
        required = False,
        source = un_klasse,
        )

    branche = Choice(
        title = u"Branche",
        description = u'Betrieb ist ein Recyclingunternehmen, ein Motorradhandel oder ein Speditions- oder Umschalgunternehmen.',
        required = True,
        source = janein,
        default = 'nein',
        )


@menuentry(NavigationMenu, order=40)
class AssignCompany(models.Edit):
    grok.context(ITeilnehmer)
    grok.name('assign_company')
    grok.title(u'Unternehmen des Teilnehmers')
    label = u"Teilnehmer"

    #fields = Fields(ITeilnehmer).select('unternehmen')
    fields = Fields(ICompany).select('unternehmen')
    fields['unternehmen'].mode = 'multiselect'

    def update(self):
        chosen_js.need()
        chosen_css.need()
        chosen_ajax.need()

    def updateWidgets(self):
        super(AssignCompany, self).updateWidgets()
        field_id = self.fieldWidgets.get('form.field.unternehmen')
        field_id.template = ChameleonPageTemplateFile('templates/select.cpt')

    def getDefaults(self):
        rc = []
        i=True
        for unt in self.context.unternehmen:
            rc.append(
                dict(
                    title="%s - %s" % (unt.mnr, unt.name),
                    value=unt.mnr,
                    disabled=i
                )
            )
            i=False
        return rc

    @action('Speichern')
    def handle_edit(self):
        data, errors = self.extractData()
        if errors:
            self.submissionError = errors
            return FAILURE
        def getUnternehmen(mnr):
            session = Session()
            return session.query(Unternehmen).get(mnr)
        data['unternehmen'] = [getUnternehmen(x) for x in list(data['unternehmen'])]
        teilnehmer = self.getContentData()
        apply_data_event(self.fields, teilnehmer, data)
        teilnehmer = teilnehmer.getContent()
        self.flash(_(u"Content updated"))
        self.redirect(self.application_url() + '?form.field.id=%s&form.action.suchen=Suchen' %teilnehmer.id)

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
                erstell_datum = data.get('erstell_datum'),
                un_klasse = data.get('un_klasse'),
                branche = data.get('branche'),
                unternehmen_mnr=self.context.unternehmen_mnr)
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
        ktn.erstell_datum = data.get('erstell_datum')
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


import json
from profilehooks import profile


class SearchTeilnehmer(grok.View):
    grok.name('search_teilnehmer')
    grok.context(IFernlehrgangApp)

    def update(self):
        self.term = self.request.form['data[q]']
        self.vocabulary = getTeilnehmerId(None)

    def render(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        session = Session()
        from fernlehrgang import models
        from sqlalchemy import func, or_, cast, String
        #res = session.query(models.Teilnehmer, models.Unternehmen).filter(
        #    models.Unternehmen.mnr == models.Teilnehmer.unternehmen_mnr,
        #    or_(
        #    cast(models.Teilnehmer.id, String).like(self.term+"%"),
        #    cast(models.Teilnehmer.unternehmen_mnr, String).like(self.term+"%"),
        #    models.Unternehmen.hbst.like(self.term+"%s"),
        #    func.concat(func.concat(models.Teilnehmer.name, " "),
        #               models.Teilnehmer.vorname
        #              ).ilike("%" + self.term + "%"))).order_by(models.Teilnehmer.name, models.Teilnehmer.vorname)

        sql = session.query(models.Teilnehmer, models.Unternehmen).filter(
            models.Unternehmen.mnr == models.Teilnehmer.unternehmen_mnr, 
            or_(
                cast(models.Teilnehmer.unternehmen_mnr, String).like(self.term +"%"),
                cast(models.Teilnehmer.id, String).like(self.term+"%"), 
                models.Unternehmen.hbst.like(self.term + "%"), 
                func.concat(func.concat(models.Teilnehmer.name, " "),
                    models.Teilnehmer.vorname).ilike("%" + self.term + "%"))).order_by(models.Teilnehmer.name, models.Teilnehmer.vorname)
        terms = []
        for x, unternehmen in sql:
            gebdat = ""
            if x.geburtsdatum:
                try:
                    gebdat = "(%s)" % x.geburtsdatum.strftime('%d.%m.%Y')
                except:
                    gebdat = ""
            terms.append({'id': x.id, 'text': "%s - %s %s %s - %s (%s)" %(x.id, x.name, x.vorname, gebdat, x.unternehmen_mnr, unternehmen.hbst)})
        return json.dumps({'q': self.term, 'results': terms})


class SearchUnternehmen(grok.View):
    grok.name('search_unternehmen')
    grok.context(IFernlehrgangApp)

    def update(self):
        self.term = self.request.form['data[q]']
        self.vocabulary = voc_unternehmen(None)

    def render(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        terms = []
        matcher = self.term.lower()
        session = Session()
        from fernlehrgang import models
        from sqlalchemy import func, or_, cast, String
        print "*" * 20
        print self.term
        res = session.query(models.Unternehmen).filter(or_(
            cast(models.Unternehmen.mnr, String).like(self.term+"%"),
            models.Unternehmen.name.like(self.term+"%")
        ))
        for x in res:
            terms.append({'id': x.mnr, 'text': "%s - %s" %(x.mnr, x.name)})
        print terms
        #for item in self.vocabulary:
        #    if matcher in item.title.lower():
        #        terms.append({'id': item.token, 'text': item.title})
        return json.dumps({'q': self.term, 'results': terms})


#    def render(self):
#        self.request.response.setHeader('Content-Type', 'application/json')
#        terms = []
#        matcher = self.term.lower()
#        for item in self.vocabulary:
#            if matcher in item.title.lower():
#                terms.append({'id': item.token, 'text': item.title})
#        return json.dumps({'q': self.term, 'results': terms})


class OverviewKurse(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(ITeilnehmer)
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
