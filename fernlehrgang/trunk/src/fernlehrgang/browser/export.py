# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from zope.interface import Interface
from dolmen.menu import menuentry, Menu
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.viewlets import NavigationMenu
from fernlehrgang.lib.interfaces import IXLSExport, IXLSReport, IXLSFortbildung
from fernlehrgang import Form
from zeam.form.base import Fields, action
from megrok.layout import Page


grok.templatedir('templates')


@menuentry(NavigationMenu)
class Exporte(Page):
    grok.context(IFernlehrgang)
    grok.title('Exporte')
    grok.order(200)


class ExportItems(Menu):
    grok.context(Interface)
    grok.title('ExportItems')


@menuentry(ExportItems)
class XSLExportForm(Form):
    grok.context(IFernlehrgang)
    grok.title('XLS-Export')

    fields = Fields(IXLSExport)

    @action(u"Export Starten")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Bitte korrigieren Sie die Fehler')
        self.redirect(self.url('xml', data=data))

@menuentry(ExportItems)
class XLSReport(grok.View):
    grok.context(IFernlehrgang)
    grok.name('xlsreport')
    grok.title('Statusliste')

    def update(self):
        self.file = IXLSReport(self.context).createXLS(self.request.form)

    def render(self):
        dateiname = "Statusliste-Fernlehrgang.xlsx"
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'application/ms-excel')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' % dateiname )
        self.file.seek(0)
        return self.file.read()


class XMLExport(grok.View):
    grok.context(IFernlehrgang)
    grok.name('xml')

    def update(self):
        from fernlehrgang.tasks import export
        form = self.request.form
        lh_id, lh = form['lehrheft'].split('-')
        fn = export.delay(self.context.id, lh_id, lh, form['rdatum'], form['stichtag'], form['dateiname']) 

    def render(self):
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())


import zope.component
from megrok.layout.interfaces import ILayout
from zope.publisher.publish import mapply

@menuentry(ExportItems)
class XLSFortbildung(Form):
    grok.context(IFernlehrgang)
    grok.name('xlsfortbildung')
    grok.title(u'Versandliste Fortbildung')
    bin_data = None

    fields = Fields(IXLSFortbildung)

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        self.updateForm()
        if self.request.response.getStatus() in (302, 303):
            return
        if self.bin_data:
            return self.asPDF() 
        self.layout = zope.component.getMultiAdapter(
            (self.request, self.context), ILayout)
        return self.layout(self) 

    @action(u"Export Starten")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(u'Fehler beheben')
            return
        xls = IXLSFortbildung(self.context)
        self.bin_data = xls.create(data)

    def asPDF(self):
        RESPONSE = self.request.response
        dateiname= "Fortbildung-Stichtag.xls"
        RESPONSE.setHeader('content-type', 'application/ms-excel')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' % dateiname )
        return self.bin_data
