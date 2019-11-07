# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.models import Fernlehrgang
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from fernlehrgang.browser import AddForm, EditForm, DefaultView

from megrok.traject import locate
from megrok.traject.components import DefaultModel
from megrok.z3ctable import GetAttrColumn, LinkColumn
from fernlehrgang.browser import TablePage
from z3c.saconfig import Session
from zeam.form.base import Fields
from grokcore.chameleon.components import ChameleonPageTemplateFile
from fernlehrgang.viewlets import NavEntry, AddEntry, ObjectEntry

grok.templatedir('templates')



class NaviEntryFlg(NavEntry):
    grok.context(IFernlehrgangApp)
    title = u"Fernlehrgänge"

    def url(self):
        return self.view.url(self.context, 'fernlehrgang_listing')


class FernlehrgangListing(TablePage):
    grok.context(IFernlehrgangApp)
    grok.name('fernlehrgang_listing')
    grok.title(u"Fernlehrgänge")
    grok.order(10)

    template = ChameleonPageTemplateFile('templates/base_listing.cpt')

    label = u"Fernlehrgänge"
    description = u"Hier können Sie die Fernlehrgänge der BG verwalten."

    cssClasses = {'table': 'table table-striped table-bordered table-condensed'}
    status = None

    @property
    def values(self):
        root = grok.getSite()
        session = Session()
        for fernlehrgang in session.query(Fernlehrgang).all():
            locate(root, fernlehrgang, DefaultModel)
            yield fernlehrgang


class AddEntryFlg(AddEntry):
    grok.context(IFernlehrgangApp)
    grok.name('addentryflg')
    title = u"Fernlehrgang"

    def url(self):
        return self.view.url(self.context, 'addfernlehrgang')


#@menuentry(AddMenu)
class AddFernlehrgang(AddForm):
    grok.context(IFernlehrgangApp)
    grok.title(u'Fernlehrgang')
    title = u'Fernlehrgang'
    label = u'Fernlehrgang anlegen'
    description = u""

    fields = Fields(IFernlehrgang).omit('id')

    def create(self, data):
        return Fernlehrgang(**data)

    def add(self, object):
        session = Session()
        session.add(object)

    def nextURL(self):
        self.flash(u'Der Fernlehrgang wurde erfolgreich angelegt.')
        url = self.url(self.context)
        return url


class DisplayEntryFlg(ObjectEntry):
    grok.context(IFernlehrgang)
    grok.name('displayflg')
    title = u"Anzeigen"

    def url(self):
        return self.view.url(self.context)

#@menuentry(NavigationMenu)
class Index(DefaultView):
    grok.title('Fernlehrgang')
    grok.context(IFernlehrgang)

    fields = Fields(IFernlehrgang).omit('id')

    @property
    def label(self):
        return u"Fernlehrgang: %s (%s)" % (
            self.context.titel, self.context.id)


class EditEntryFlg(ObjectEntry):
    grok.context(IFernlehrgang)
    grok.name('edit_entry_flg')
    title = u"Bearbeiten"

    def url(self):
        return self.view.url(self.context, 'edit')


class Edit(EditForm):
    grok.context(IFernlehrgang)

    label = u"Fernlehrgang bearbeiten"
    description = u"Hier können Sie Ihren Fernlehrgang bearbeiten"
    fields = Fields(IFernlehrgang).omit('id')


# Spalten

class ID(GetAttrColumn):
    grok.name('Id')
    grok.context(IFernlehrgangApp)
    weight = 5
    header = u"Id"
    attrName = u"id"


class Title(LinkColumn):
    grok.name('titel')
    grok.context(IFernlehrgangApp)
    weight = 10
    header = u"Titel"
    attrName = u"titel"

    def getLinkContent(self, item):
        return item.titel


class Jahr(GetAttrColumn):
    grok.name('Jahr')
    grok.context(IFernlehrgangApp)
    weight = 20
    header = u"Jahr"
    attrName = u"jahr"


class Typ(GetAttrColumn):
    grok.name('Typ')
    grok.context(IFernlehrgangApp)
    weight = 15 
    header = u"Typ"

    def renderCell(self, item):
        from fernlehrgang.interfaces.flg import typ
        if item.typ:
            return typ(None).getTerm(item.typ).title
        return "N/A"
            
