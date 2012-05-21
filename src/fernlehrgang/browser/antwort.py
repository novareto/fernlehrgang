# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvc.layout

from fernlehrgang.interfaces import IListing
from dolmen.app.layout import IDisplayView
from dolmen.app.layout import models
from dolmen.menu import menuentry
from fernlehrgang.interfaces.antwort import IAntwort
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.models import Antwort, Frage
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable.components import TablePage, GetAttrColumn, LinkColumn, Column
from sqlalchemy import not_, and_
from z3c.saconfig import Session
from zeam.form.base import Fields, action
from uvc.layout.interfaces import IExtraInfo
from megrok.layout import Page
from grokcore.chameleon.components import ChameleonPageTemplateFile

grok.templatedir('templates')


#@menuentry(NavigationMenu)
class AntwortListing(TablePage):
    grok.implements(IDisplayView, IListing)
    grok.context(IKursteilnehmer)
    grok.name('antwort_listing')
    grok.title(u'Antworten verwalten')
    grok.baseclass()

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Antworten"
    description = u"Hier können Sie die Antworten des Kursteilnehmers korrigieren."

    @property
    def values(self):
        rc = []
        root = grok.getSite()
        for x in self.context.antworten:
            locate(root, x, DefaultModel)
            rc.append(x)
        return sorted(rc, key=lambda antwort: antwort.frage.frage)


@menuentry(AddMenu)
class AddAntwort(uvc.layout.AddForm):
    grok.context(IKursteilnehmer)
    grok.title(u'Antwort')
    label = u'Antwort anlegen'

    fields = Fields(IAntwort).omit('id')

    def create(self, data):
        return Antwort(**data)

    def add(self, object):
        self.object = object
        self.context.antworten.append(object)

    def nextURL(self):
        return self.url(self.context, 'antwort_listing')


from zeam.form.table import SubTableForm, TableActions
from zeam.form.composed import ComposedForm
from zeam.form.base import Action, SUCCESS, Actions

class SaveTableAction(Action):

       def __call__(self, form, content, line):
           setattr(content, 'antwortschema', line.extractData(form.tableFields)[0].get('antwortschema', ''))
           form.context.antworten.append(content)


@menuentry(AddMenu)
class AddAntworten(ComposedForm, uvc.layout.Form):
    grok.context(IKursteilnehmer)
    grok.title(u'Alle Antworten eingeben')
    label = u"Alle Antworten eingeben"


class AddAntwortenTable(SubTableForm):
    grok.title(u'Table Form')
    grok.context(IKursteilnehmer)
    grok.view(AddAntworten)
    prefix = "G"

    ignoreContent = False
    tableFields = Fields(IAntwort).omit('id', 'datum', 'system')
    tableActions = TableActions(SaveTableAction('Speichern'))

    def checkAntwort(self, lehrheft_id, frage_id):
        for antwort in self.context.antworten:
            if antwort.frage_id == frage_id and antwort.lehrheft_id == lehrheft_id:
                return antwort

    def getItems(self):
        rc = []
        for lehrheft in self.context.fernlehrgang.lehrhefte:
            for frage in lehrheft.fragen:
                antwort = self.checkAntwort(lehrheft.id, frage.id)
                if antwort:
                    rc.append(antwort)
                else:
                    rc.append(Antwort(
                        lehrheft_id = lehrheft.id,
                        frage_id = frage.id, 
                        antwortschema = u"",
                        system = u"FernlehrgangApp", 
                        ))
        return rc


class Index(models.DefaultView):
    grok.context(IAntwort)
    grok.title(u'Index')
    title = label = u"Antwort"
    description = u"" #Hier können Sie Deteils zu Ihren Antworten ansehen."

    fields = Fields(IAntwort).omit('id')


class Edit(models.Edit):
    grok.context(IAntwort)
    grok.title(u'Edit')
    grok.name('edit')
    title = u"Antworten"
    description = u"Hier können Sie die Antwort bearbeiten."

    fields = Fields(IAntwort).omit('id')
    fields['lehrheft_id'].mode = "hiddendisplay"
    fields['frage_id'].mode = "hiddendisplay"


### ExtraInfo

class MoireInfoOnKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IAntwort)
    script = ""

    def update(self):
        url = grok.url(self.request, self.context.kursteilnehmer)
        self.script = "<script> var base_url = '%s'; </script>" % url

    def render(self):
        return self.script


class JSON_Views(grok.JSON):
    """ Ajax basiertes Wechseln der Jahre"""
    grok.context(IKursteilnehmer)
 
    def context_fragen(self, lehrheft_id=None):
        rc = []
        li = []
        session = Session()
        i=0
        for antwort in [x for x in self.context.antworten]:
            li.append(antwort.frage.id)
        for id, nr, titel in session.query(Frage.id, Frage.frage, Frage.titel).filter(
                                           and_(Frage.lehrheft_id == int(lehrheft_id),
                                                not_(Frage.id.in_(li)))).all():
            rc.append('<option id="form-widgets-frage_id-%s" value=%s> %s - %s </option>' %(i, id, nr, titel))
            i+=1
        return {'fragen': ''.join(rc)}


### Spalten

class Link(LinkColumn):
    grok.name('Nummer')
    grok.context(IKursteilnehmer)
    weight = 5
    linkContent = "edit"

    def getSortKey(self, item):
        return int(item.frage.lehrheft.nummer+item.frage.frage.zfill(2))

    def getLinkContent(self, item):
        return u"Antwort auf Frage '%s'; %s" %(item.frage.frage, item.frage.titel)


class Lehrheft(Column):
    grok.name('Lehrheft')
    grok.context(IKursteilnehmer)
    weight = 9
    header = "Lehrheft"

    def renderCell(self, item):
        return item.frage.lehrheft.nummer


class Antworten(GetAttrColumn):
    grok.name('Antworten')
    grok.context(IKursteilnehmer)
    weight = 10
    header = "Antworten"
    attrName = "antwortschema"



@menuentry(NavigationMenu)
class OverviewAntworten(Page):
    grok.implements(IDisplayView, IListing)
    grok.context(IKursteilnehmer)
    grok.name('antwort_listing')
    grok.title(u'Antworten verwalten')

    label = title = u"Antworten"
    description = u"Hier können Sie die Antworten des Kursteilnehmers korrigieren."

    def getResults(self):
        context = self.context
        rc = []
        for lehrheft in context.fernlehrgang.lehrhefte:
            res = dict()
            res['titel'] = "%s - %s" %(lehrheft.nummer, lehrheft.titel)
            lehrheft_id = lehrheft.id
            fragen = []
            for antwort in context.antworten:
                if antwort.frage.lehrheft_id == lehrheft_id:
                    titel = u"Antwort auf Frage '%s'; '%s'" %(antwort.frage.frage, antwort.frage.titel)
                    url = "%s/antwort/%s" % (self.url(self.context), antwort.id)
                    d=dict(titel = titel,
                           url = url, 
                           lehrheft_nr = lehrheft.nummer, 
                           aw = antwort.antwortschema)
                    fragen.append(d)
            res['antworten'] = fragen
            rc.append(res)
        return rc
