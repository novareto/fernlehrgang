# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


from uvclight import Action, Actions, SUCCESS, FAILURE
from dolmen.forms.crud import Delete
from dolmen.forms.crud import actions as formactions, i18n as _
from z3c.saconfig import Session


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


class Delete(Delete):
    actions = Actions(RDBDeleteAction(_("Delete")),
                      formactions.CancelAction(_("Cancel")))

