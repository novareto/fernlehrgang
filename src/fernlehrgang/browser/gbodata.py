# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok

from fernlehrgang import Form
from zeam.form.base import Fields
from zeam.form.base import action
from megrok.traject import locate
from fernlehrgang.models import GBOData
from dolmen.menu import Entry, menu, menuentry
from fernlehrgang.interfaces.gbo import IGBOData
from dolmen.app.layout import models, IDisplayView
from fernlehrgang.viewlets import AddMenu, NavigationMenu
from fernlehrgang.interfaces.unternehmen import IUnternehmen


@menuentry(AddMenu)
class AddBGODaten(Form):
    grok.context(IUnternehmen)
    grok.title(u'GBO-Daten')
    label = u'GBO-Daten anlegen'
    description = u'GOD-Daten anlegen'

    fields = Fields(IGBOData).omit('id')

    @action(u'Anlegen')
    def handleSearch(self):
        data, errors = self.extractData()
        if errors:
            return
        gd = GBOData(**data)
        self.context.goddata.append(gd)
        self.redirect(self.url(self.context, 'index'))


class GodMenu(Entry):
    grok.implements(IDisplayView)
    menu(NavigationMenu)
    grok.context(IUnternehmen)
    grok.order(20)

    @property
    def title(self):
        return "GBO-DATEN"

    @property
    def url(self):
        if self.context.gbodata:
            return "%s/goddata/%s" % (self.context.mnr, self.context.gbodata.id)
        return ""


class Index(models.DefaultView):
    grok.context(IGBOData)
    grok.title(u'View')
    title = label = u"God-Daten"
    description = u"Details GOD-Daten"

    fields = Fields(IGBOData).omit(id)


class Edit(models.Edit):
    grok.context(IGBOData)
    grok.name('edit')
    grok.title(u'Edit')

    fields = Fields(IGBOData).omit('id')
    fields['branche'].mode = "radio"
