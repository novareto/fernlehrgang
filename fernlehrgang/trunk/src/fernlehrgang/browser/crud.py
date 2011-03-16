# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c.saconfig import Session
from dolmen.app.layout import Delete
from dolmen.forms.crud.actions import DeleteAction
from zeam.form.base import Actions
from dolmen.forms.crud import actions as formactions, i18n as _
from zeam.form.base.markers import SUCCESS, FAILURE


class RDBDeleteAction(DeleteAction):

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


class Delete(Delete):
    actions = Actions(RDBDeleteAction(_("Delete")),
                      formactions.CancelAction(_("Cancel")))

