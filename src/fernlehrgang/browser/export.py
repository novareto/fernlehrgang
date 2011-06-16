# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from dolmen.menu import menuentry
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.viewlets import NavigationMenu
from fernlehrgang.export import IXLSExport
from uvc.layout import Form
from zeam.form.base import Fields, action


@menuentry(NavigationMenu)
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



class XMLExport(grok.View):
    grok.context(IFernlehrgang)
    grok.name('xml')

    def update(self):
        self.file = IXLSExport(self.context).createXLS(self.request.form)

    def render(self):
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'application/vnd.ms-excel')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=flgadressen.xls')
        self.file.seek(0)
        return self.file.read()
