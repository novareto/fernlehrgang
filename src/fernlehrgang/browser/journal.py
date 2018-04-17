# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from dolmen.app.layout import models, IDisplayView
from dolmen.forms.base.utils import set_fields_data, apply_data_event
from dolmen.forms.crud import i18n as _
from dolmen.menu import menuentry, Entry, menu
from fernlehrgang import Form, AddForm
from fernlehrgang import fmtDate
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.journal import IJournalEntry
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.models import JournalEntry
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


@menuentry(NavigationMenu, order=20)
class JournalListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(ITeilnehmer)
    grok.name('journal_listing')
    grok.title(u'Journal')

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')
    description = "Journal"

    label = u"Journal"
    batchSize = 150
    startBatchingAt = 150
    cssClasses = {
        'table': 'table table-striped table-bordered table-condensed'}

    @property
    def values(self):
        return self.context.journal_entries


class ID(LinkColumn):
    grok.name('Id')
    grok.context(ITeilnehmer)
    weight = 5
    header = u"Id"
    attrName = "id"

    def getLinkURL(self, item):
        return self.table.url().replace('_listing', '/' + str(item.id))

    def getLinkContent(self, item):
        return item.id


class Status(Column):
    grok.name('Status')
    grok.context(ITeilnehmer)
    weight = 30
    header = u"Status"
    attrName = "status"

    def renderCell(self, item):
        from fernlehrgang.interfaces.journal import get_status
        source = get_status(None)
        import pdb; pdb.set_trace()
        return source.getTerm(getattr(item, 'status', '1')).title


class Type(Column):
    grok.name('Type')
    grok.context(ITeilnehmer)
    weight = 20
    header = u"Type"
    attrName = "type"

    def renderCell(self, item):
        return getattr(item, 'type', '')


class Date(Column):
    grok.name('Date')
    grok.context(ITeilnehmer)
    weight = 10
    header = u"Date"

    def renderCell(self, item):
        if item.date is not None:
            return fmtDate(item.date)
        return ""


@menuentry(AddMenu)
class AddJournalEntry(AddForm):
    grok.context(ITeilnehmer)
    grok.title(u'Journal Eintrag')
    label = u'Journal entry'

    fields = Fields(IJournalEntry).omit('id', 'teilnehmer_id', 'date')

    def create(self, data):
        entry = JournalEntry(**data)
        entry.teilnehmer_id = self.context.id
        return entry

    def add(self, entry):
        session = Session()
        session.add(entry)

    def nextURL(self):
        self.flash(u'Journal entry added')
        return "%s/journal_listing" % self.url()


@menuentry(NavigationMenu, order=40)
class EditJournalEntry(models.Edit):
    grok.name('edit')
    grok.context(IJournalEntry)
    grok.title(u'Journal')
    label = u'Journal entry'

    fields = Fields(IJournalEntry).omit('id', 'teilnehmer_id', 'date')

    @action('Speichern')
    def handle_edit(self):
        data, errors = self.extractData()
        apply_data_event(self.fields, self.getContentData(), data)
        self.flash(_(u"Content updated"))
        self.redirect(self.url(self.context))

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash(u'Ihre Aktion wurde abgebrochen.')
        self.redirect(self.url(self.context))


@menuentry(NavigationMenu, order=40)
class DeleteJournalEntry(models.Form):
    grok.name('delete')
    grok.context(IJournalEntry)
    grok.title(u'Journal entry')
    label = u'Journal entry'

    fields = Fields()

    @action('Delete')
    def handle_delete(self):
        session = Session()
        session.remove(self.context)
        self.redirect(self.url(self.context.__parent__))

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash(u'Ihre Aktion wurde abgebrochen.')
        self.redirect(self.url(self.context))
