# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from zope.interface import Interface
from dolmen.menu import menuentry, Menu
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.viewlets import NavigationMenu
from fernlehrgang.lib.export import IXLSExport, IXLSReport
from uvc.layout import Form
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
        self.file = IXLSExport(self.context).createXLS(self.request.form)

    def render(self):
        dateiname = self.request.form.get('dateiname', 'flg.xls')
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'application/ms-excel')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' % dateiname )
        self.file.seek(0)
        return self.file.read()


