# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de


from uvclight import DeleteForm, Action, Actions, SUCCESS, FAILURE
from dolmen.forms.crud import actions as formactions, i18n as _
from cromlech.sqlalchemy import get_session


class RDBDeleteAction(Action):
    failureMessage = u"Da ist was schief gelaufen"
    successMessage = u"Das Dokument wurde erfolgreich entfernt"

    def __call__(self, form):
        context = form.context
        session = get_session('fernlehrgang')
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


class Delete(DeleteForm):
    actions = Actions(RDBDeleteAction(_("Delete")),
                      formactions.CancelAction(_("Cancel")))
