# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from dolmen.app.layout import models, IDisplayView
from dolmen.menu import menuentry
from fernlehrgang.interfaces.god import IGodData
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.models import GodData
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from zeam.form.base import Fields
from zeam.form.base import action
from fernlehrgang import Form


@menuentry(AddMenu)
class AddKursteilnehmer(Form):
    grok.context(IUnternehmen)
    grok.title(u'GOD-Daten')
    label = u'GOD-Daten anlegen'
    description = u'GOD-Daten anlegen'

    fields = Fields(IGodData).omit('id')

    @action(u'Anlegen')
    def handleSearch(self):
        data, errors = self.extractData()
        if errors:
            return
        gd = GodData(**data)
        self.context.goddata.append(gd)
        self.redirect(self.url(self.context, 'index'))


from megrok.traject import locate
from uvc.layout import Page

from dolmen.menu import Entry, menu
class GodMenu(Entry):
    grok.implements(IDisplayView)
    menu(NavigationMenu)
    grok.context(IUnternehmen)

    @property
    def title(self):
        return "GOD-DATEN"

    @property
    def url(self):
        return "%s/goddata/%s" % (self.context.mnr, self.context.goddata[0].id)


class Index(models.DefaultView):
    grok.context(IGodData)
    grok.title(u'View')
    title = label = u"God-Daten"
    description = u"Details GOD-Daten"

    fields = Fields(IGodData).omit(id)


class Edit(models.Edit):
    grok.context(IGodData)
    grok.name('edit')
    grok.title(u'Edit')

    fields = Fields(IGodData).omit('id')
    fields['branche'].mode = "radio"
