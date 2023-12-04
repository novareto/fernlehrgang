# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
from datetime import datetime
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable.components import GetAttrColumn, LinkColumn, Column
from sqlalchemy import not_, and_
from z3c.saconfig import Session
from zeam.form.base import Action
from zeam.form.base import Fields
from zeam.form.composed import ComposedForm
from zeam.form.table import SubTableForm, TableActions
from zope.interface import implementer

from fernlehrgang.browser import AddForm, Form, TablePage, Page, DefaultView, EditForm
from fernlehrgang.interfaces import IListing
from fernlehrgang.interfaces.antwort import IAntwort
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.models import Antwort, Frage
from fernlehrgang.viewlets import NavEntry
from fernlehrgang.viewlets import AddEntry


grok.templatedir("templates")


class KTNAntwortEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.order(14)
    grok.name("ktnantwortentry")

    title = "Antworten verwalten"
    icon = "fas fa-check-circle"

    def url(self):
        return self.view.url(self.context, "antwort_listing")


@implementer(IListing)
class AntwortListing(TablePage):
    grok.context(IKursteilnehmer)
    grok.name("antwort_listing")
    grok.title("Antworten verwalten")
    grok.baseclass()

    template = ChameleonPageTemplateFile("templates/base_listing.cpt")

    label = "Antworten"
    description = "Hier können Sie die Antworten des Kursteilnehmers korrigieren."

    @property
    def values(self):
        rc = []
        root = grok.getSite()
        for x in self.context.antworten:
            locate(root, x, DefaultModel)
            rc.append(x)
        return sorted(rc, key=lambda antwort: antwort.frage.frage)


class AddEntryAntwort(AddEntry):
    grok.context(IKursteilnehmer)
    grok.name("addquestionan")
    grok.require("zope.View")
    title = "Antworte eingeben"

    def url(self):
        return self.view.url(self.context, "addantwort")


class AddAntwort(AddForm):
    grok.context(IKursteilnehmer)
    grok.title("Antwort")

    label = "Antwort anlegen"
    fields = Fields(IAntwort).omit("id", "gbo", "gbo_daten")

    def create(self, data):
        return Antwort(**data)

    def add(self, object):
        self.object = object
        self.context.antworten.append(object)

    def nextURL(self):
        return self.url(self.context, "antwort_listing")


class SaveTableAction(Action):
    postOnly = False

    def __call__(self, form, content, line):
        setattr(
            content,
            "antwortschema",
            line.extractData(form.tableFields)[0].get("antwortschema", ""),
        )
        form.context.antworten.append(content)
        form.redirect(form.url() + "/addantworten")


# @menuentry(AddMenu)
class AddEntryAntworten(AddEntry):
    grok.context(IKursteilnehmer)
    grok.name("addquestionanall")
    grok.require("zope.View")
    title = "Alle Antworten"

    def url(self):
        return self.view.url(self.context, "addantworten")


class AddAntworten(ComposedForm, Form):
    grok.context(IKursteilnehmer)
    grok.title("Alle Antworten eingeben")
    label = "Alle Antworten eingeben"

    def __init__(self, context, request):
        super(AddAntworten, self).__init__(context, request)
        self.subforms = self.allSubforms
        print(self.subforms, self.allSubforms)


class LHDummy(object):
    id = None
    title = "Bitte Auswahl Treffen"
    fragen = []


class AddAntwortenTable(SubTableForm):
    grok.title("Table Form")
    grok.context(IKursteilnehmer)
    grok.view(AddAntworten)
    prefix = "G"
    template = ChameleonPageTemplateFile("templates/alleantworten.cpt")

    ignoreContent = False
    tableFields = Fields(IAntwort).omit("id", "datum", "system", "gbo", "gbo_daten")
    tableActions = TableActions(SaveTableAction("Speichern"))

    def checkAntwort(self, lehrheft_id, frage_id):
        for antwort in self.context.antworten:
            if antwort.frage_id == frage_id and antwort.lehrheft_id == lehrheft_id:
                return antwort

    def getItems(self):
        rc = []
        lehrhefte = self.lehrhefte
        lh_id = self.request.get("lh_id") or self.request.get("select_lehrhefte")
        if lh_id:
            lehrhefte = [lh for lh in lehrhefte if str(lh.id) == lh_id]
        for lehrheft in lehrhefte:
            for frage in sorted(lehrheft.fragen, key=lambda frage: int(frage.frage)):
                antwort = self.checkAntwort(lehrheft.id, frage.id)
                if antwort:
                    rc.append(antwort)
                else:
                    rc.append(
                        Antwort(
                            lehrheft_id=lehrheft.id,
                            frage_id=frage.id,
                            antwortschema="",
                            datum=datetime.now(),
                            system="FernlehrgangApp",
                        )
                    )
        return rc

    @property
    def lehrhefte(self):
        return [LHDummy()] + self.context.fernlehrgang.lehrhefte

    @property
    def script(self):
        return "<script> var base_url = '%s/addantworten'; </script>" % self.url()


class Index(DefaultView):
    grok.context(IAntwort)
    grok.title("Index")
    title = label = "Antwort"
    description = ""  # Hier können Sie Deteils zu Ihren Antworten ansehen."

    fields = Fields(IAntwort).omit("id")


class Edit(EditForm):
    grok.context(IAntwort)
    grok.title("Edit")
    grok.name("edit")

    title = "Antworten"
    description = "Hier können Sie die Antwort bearbeiten."

    fields = Fields(IAntwort).omit("id")
    fields["lehrheft_id"].mode = "hiddendisplay"
    fields["frage_id"].mode = "hiddendisplay"

    def update(self):
        self.context.datum = datetime.now()


class JSON_Views(grok.JSON):
    """Ajax basiertes Wechseln der Jahre"""

    grok.context(IKursteilnehmer)

    def context_fragen(self, lehrheft_id=None):
        rc = []
        li = []
        session = Session()
        i = 0
        for antwort in [x for x in self.context.antworten]:
            li.append(antwort.frage.id)
        for id, nr, titel in (
            session.query(Frage.id, Frage.frage, Frage.titel)
            .filter(and_(Frage.lehrheft_id == int(lehrheft_id), not_(Frage.id.in_(li))))
            .all()
        ):
            rc.append(
                '<option id="form-widgets-frage_id-%s" value=%s> %s - %s </option>'
                % (i, id, nr, titel)
            )
            i += 1
        return {"fragen": "".join(rc)}


class Link(LinkColumn):
    grok.name("Nummer")
    grok.context(IKursteilnehmer)
    weight = 5
    linkContent = "edit"

    def getSortKey(self, item):
        return int(item.frage.lehrheft.nummer + item.frage.frage.zfill(2))

    def getLinkContent(self, item):
        return "Antwort auf Frage '%s'; %s" % (item.frage.frage, item.frage.titel)


class Lehrheft(Column):
    grok.name("Lehrheft")
    grok.context(IKursteilnehmer)
    weight = 9
    header = "Lehrheft"

    def renderCell(self, item):
        return item.frage.lehrheft.nummer


class Antworten(GetAttrColumn):
    grok.name("Antworten")
    grok.context(IKursteilnehmer)
    weight = 10
    header = "Antworten"
    attrName = "antwortschema"


# @menuentry(NavigationMenu)
@implementer(IListing)
class OverviewAntworten(Page):
    grok.context(IKursteilnehmer)
    grok.name("antwort_listing")
    grok.title("Antworten verwalten")

    label = title = "Antworten"
    description = "Hier können Sie die Antworten des Kursteilnehmers korrigieren."

    def getResults(self):
        context = self.context
        rc = []
        for lehrheft in context.fernlehrgang.lehrhefte:
            res = dict()
            res["titel"] = "%s - %s -%s" % (
                lehrheft.nummer,
                lehrheft.titel,
                lehrheft.id,
            )
            lehrheft_id = lehrheft.id
            fragen = []
            for antwort in context.antworten:
                if antwort.frage.lehrheft_id == lehrheft_id:
                    titel = "Antwort auf Frage '%s'; '%s'" % (
                        antwort.frage.frage,
                        antwort.frage.titel,
                    )
                    url = "%s/antwort/%s" % (self.url(self.context), antwort.id)
                    d = dict(
                        titel=titel,
                        url=url,
                        lehrheft_nr=lehrheft.nummer,
                        aw=antwort.antwortschema,
                    )
                    fragen.append(d)
            res["antworten"] = fragen
            rc.append(res)
        return rc
