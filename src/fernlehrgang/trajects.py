# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from megrok import traject
from z3c.saconfig import Session
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.models import Fernlehrgang


class FernlehrgangTraject(traject.Traject):
    grok.context(IFernlehrgangApp)

    pattern = "fernlehrgang/:fernlehrgang_id"
    model = Fernlehrgang

    def factory(fernlehrgang_id):
        session = Session()
        return session.query(Fernlehrgang).filter(Fernlehrgang.id == int(fernlehrgang_id)).one()

    def arguments(user):
        return dict(fernlehrgang_id = fernlehrgang.id)
