# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from datetime import datetime
from dolmen.menu import menuentry

from fernlehrgang.models import Antwort, Frage
from uvclight.interfaces import IExtraInfo
from sqlalchemy import not_, and_
from cromlech.sqlalchemy import get_session
from dolmen.forms.base import Action, Fields, INPUT, FAILURE, SUCCESS
from dolmen.forms.base.errors import Error
from dolmen.forms.base.utils import set_fields_data
from dolmen.forms.composed import ComposedForm
from dolmen.forms.table import SubTableForm, TableActions

from ..wsgi import IFernlehrgangSkin, model_lookup
from .viewlets import AddMenu, NavigationMenu
from ..interfaces import IListing, IAntwort, IKursteilnehmer


@menuentry(AddMenu)
class AddAntwort(uvclight.AddForm):
    uvclight.context(IKursteilnehmer)
    uvclight.title(u'Antwort')
    uvclight.layer(IFernlehrgangSkin)

    label = u'Antwort anlegen'
    fields = uvclight.Fields(IAntwort).omit('id')

    def create(self, data):
        return Antwort(**data)

    def add(self, object):
        self.object = object
        self.context.antworten.append(object)

    def nextURL(self):
        return self.url(self.context, 'antwort_listing')


class SaveTableAction(Action):

    def __call__(self, form, content, line):
        setattr(content, 'antwortschema',
                line.extractData(
                    form.tableFields)[0].get('antwortschema', ''))
        form.context.antworten.append(content)
        form.redirect(form.url() + '/addantworten')


from dolmen.forms.table import TableForm


class LHDummy(object):
    id = None
    title = u"Bitte Auswahl Treffen"
    fragen = []


@menuentry(AddMenu)
class AddAntworten(TableForm, uvclight.Form):
    uvclight.context(IKursteilnehmer)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.title(u'Alle Antworten eingeben')
    template = uvclight.get_template('alleantworten.cpt', __file__)

    label = u"Alle Antworten eingeben"
    tableFields = uvclight.Fields(IAntwort).omit('id', 'datum', 'system')
    tableFields['antwortschema'].mode = INPUT
    ignoreContent = False
    ignoreRequest = False
    
    def checkAntwort(self, lehrheft_id, frage_id):
        for antwort in self.context.antworten:
            if antwort.frage_id == frage_id and antwort.lehrheft_id == lehrheft_id:
                return antwort

    def getItems(self):
        rc = []
        lehrhefte = self.lehrhefte
        lh_id = self.request.form.get('lh_id') or self.request.form.get('select_lehrhefte')
        if lh_id:
            lehrhefte = [lh for lh in lehrhefte if str(lh.id) == lh_id]
        for lehrheft in lehrhefte:
            for frage in sorted(lehrheft.fragen, key=lambda frage: int(frage.frage)):
                antwort = self.checkAntwort(lehrheft.id, frage.id)
                if antwort:
                    rc.append(antwort)
                else:
                    rc.append(Antwort(
                        lehrheft_id=lehrheft.id,
                        frage_id=frage.id,
                        antwortschema=u"",
                        datum=datetime.now(),
                        system=u"FernlehrgangApp",
                        kursteilnehmer=self.context,
                        ))
        return rc

    @property
    def lehrhefte(self):
        return [LHDummy()] + self.context.fernlehrgang.lehrhefte

    @property
    def script(self):
        return "<script> var base_url = '%s/addantworten'; </script>" % self.url(self.context)

    @uvclight.action('Speichern')
    def handle_save(self):
        data, errors = self.extractData(self.fields)
        if errors:
            self.errors = errors
            return FAILURE

        self.updateLines(mark_selected=True)

        altered = []
        for l in self.lines:
            if l.selected:
                line_data, line_errors = l.extractData(self.tableFields.select("antwortschema"))
                if line_errors:
                    errors.extend(line_errors)
                else:
                    altered.append((l.getContent(), line_data))

        if not altered:
            errors.append(Error('Please, select at least one entry', self.prefix))

        if errors:
            self.errors = errors
            return FAILURE
        
        for line, line_data in altered:
            set_fields_data(self.tableFields, line, line_data)

        return SUCCESS

class Index(uvclight.DefaultView):
    uvclight.context(IAntwort)
    uvclight.title(u'Index')
    uvclight.layer(IFernlehrgangSkin)

    title = label = u"Antwort"
    description = u""  # Hier können Sie Deteils zu Ihren Antworten ansehen."
    fields = Fields(IAntwort).omit('id')


class Edit(uvclight.EditForm):
    uvclight.context(IAntwort)
    uvclight.title(u'Edit')
    uvclight.name('edit')
    uvclight.layer(IFernlehrgangSkin)

    title = u"Antworten"
    description = u"Hier können Sie die Antwort bearbeiten."

    fields = Fields(IAntwort).omit('id')
    fields['lehrheft_id'].mode = "hiddendisplay"
    fields['frage_id'].mode = "hiddendisplay"

    def update(self):
        self.context.datum = datetime.now()


from .crud import Delete
class Delete(Delete):
    uvclight.context(IAntwort)
    uvclight.layer(IFernlehrgangSkin)


### ExtraInfo

class MoireInfoOnKursteilnehmer(uvclight.Viewlet):
    uvclight.viewletmanager(IExtraInfo)
    uvclight.context(IAntwort)
    uvclight.layer(IFernlehrgangSkin)

    script = ""

    def update(self):
        url = self.view.url(self.context.kursteilnehmer)
        self.script = "<script> var base_url = '%s'; </script>" % url

    def render(self):
        return self.script


class Context_Fragen(uvclight.JSON):
    """ Ajax basiertes Wechseln der Jahre"""
    uvclight.context(IKursteilnehmer)
    uvclight.name('context_fragen')

    def render(self):
        lehrheft_id = self.request.form.get('lehrheft_id', None)
        rc = []
        li = []
        session = get_session('fernlehrgang')
        i = 0
        for antwort in [x for x in self.context.antworten]:
            li.append(antwort.frage.id)
        for id, nr, titel in session.query(
            Frage.id, Frage.frage, Frage.titel).filter(
                and_(Frage.lehrheft_id == int(lehrheft_id),
                not_(Frage.id.in_(li)))
            ).all():
            rc.append('<option id="form-widgets-frage_id-%s" value=%s> %s - %s </option>' %(i, id, nr, titel))
            i += 1
        return {'fragen': ''.join(rc)}


### Spalten

class Link(uvclight.LinkColumn):
    uvclight.name('Nummer')
    uvclight.context(IKursteilnehmer)
    weight = 5
    linkContent = "edit"

    def getSortKey(self, item):
        return int(item.frage.lehrheft.nummer + item.frage.frage.zfill(2))

    def getLinkContent(self, item):
        return u"Antwort auf Frage '%s'; %s" %(item.frage.frage, item.frage.titel)


class Lehrheft(uvclight.Column):
    uvclight.name('Lehrheft')
    uvclight.context(IKursteilnehmer)
    weight = 9
    header = "Lehrheft"

    def renderCell(self, item):
        return item.frage.lehrheft.nummer


class Antworten(uvclight.GetAttrColumn):
    uvclight.name('Antworten')
    uvclight.context(IKursteilnehmer)
    weight = 10
    header = "Antworten"
    attrName = "antwortschema"


@menuentry(NavigationMenu)
class OverviewAntworten(uvclight.Page):
    uvclight.implements(IListing)
    uvclight.context(IKursteilnehmer)
    uvclight.name('antwort_listing')
    uvclight.title(u'Antworten verwalten')
    uvclight.layer(IFernlehrgangSkin)

    template = uvclight.get_template('overviewantworten.cpt', __file__)

    label = title = u"Antworten"
    description = u"Hier können Sie die Antworten des Kursteilnehmers korrigieren."

    def getResults(self):
        context = self.context
        rc = []
        for lehrheft in context.fernlehrgang.lehrhefte:
            res = dict()
            res['titel'] = "%s - %s -%s" %(lehrheft.nummer, lehrheft.titel, lehrheft.id)
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
