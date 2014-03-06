# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import uvclight

from zope.interface import Interface
from fernlehrgang.models.fernlehrgang import IFernlehrgang
from fernlehrgang.app.browser.viewlets import NavigationMenu


@uvclight.menuentry(NavigationMenu, order=200)
class Exporte(uvclight.Page):
    uvclight.context(IFernlehrgang)
    uvclight.title(u'Versandlisten')
    uvclight.order(200)
    #uvclight.require('dolmen.content.Add')
    template = uvclight.get_template('exporte.cpt', __file__)


class ExportItems(uvclight.Menu):
    uvclight.context(Interface)
    uvclight.title('ExportItems')
