# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from zeam.form.base import Actions, Action
from zeam.form.base.markers import SUCCESS, FAILURE


class RDBDeleteAction(Action):

    def __call__(self, form):
        context = form.context
        session = Session()
        try:
            session.delete(context)
            form.status = self.successMessage
            form.flash(form.status)
            form.redirect(form.url(context.__parent__))
            return SUCCESS
        except:
            pass
        form.status = self.failureMessage
        form.flash(form.status)
        form.redirect(form.url(form.context))
        return FAILURE


class Delete(Action):
    actions = Actions(RDBDeleteAction("Delete"),)

