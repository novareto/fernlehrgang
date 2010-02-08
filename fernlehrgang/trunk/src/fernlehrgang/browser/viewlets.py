# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from fernlehrgang.models import Fernlehrgang
from zope.interface import Interface
from uvc.layout.interfaces import IGlobalMenu



class GlobalMenu(grok.ViewletManager):
    grok.name('uvcsite.globalmenu')
    grok.context(Interface)
    grok.implements(IGlobalMenu)
    template = grok.PageTemplateFile('globalmenu.pt')

    css = ['blue', 'orange', 'violet', 'green', 'brown', 'purple']

    def getClass(self, index):
        return self.css[index]

    @property
    def flgs(self):
        session = Session()
        rc = []
        for i, fernlehrgang in enumerate(session.query(Fernlehrgang).all()):
            url = "%s/fernlehrgang/%s" %(self.view.application_url(), fernlehrgang.id)
            rc.append(dict(title=fernlehrgang.jahr, css=self.css[i], url=url))
        return rc    



