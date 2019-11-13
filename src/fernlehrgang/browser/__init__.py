# package

import grok
import grokcore.message
import logging
import zeam.form.base
import zope.lifecycleevent

from grok import baseclass, View as BaseView
from grok import getApplication
from grok import url
from grok.components import ViewSupportMixin
from grok.interfaces import IGrokView
from grokcore.layout import Page as BasePage
from grokcore.layout.components import LayoutAware
from grokcore.chameleon.components import ChameleonPageTemplateFile
from megrok.z3ctable import TablePage
from zeam.form import base
from zeam.form.base import DISPLAY, Action, Actions, FAILURE, SUCCESS
from zeam.form.layout import Form
from zeam.form.ztk.widgets.date import DateField
from zeam.form.ztk.actions import CancelAction
from zope.interface import implementer
from .utils import apply_data_event

grok.templatedir('templates')


DateField.valueLength = "medium"


class UpdateAction(Action):
    """Update action for any locatable object.
    """

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.submissionError = errors
            return FAILURE

        apply_data_event(form.fields, form.getContentData(), data)
        form.flash(u"Content updated")
        form.redirect(form.url(form.context))

        return SUCCESS


class Form(Form, LayoutAware):
    grok.baseclass()

    classes = {
        'group': 'form-group',
        'group-error': 'form-group alert-danger has-error',
        'field': ['form-control'],
        'field-error': ['form-control', 'is-invalid'],
        'button': 'action btn',
    }

    def updateWidgets(self):
        super().updateWidgets()
        for widget in self.fieldWidgets:
            if widget.error:
                widget.htmlClass = lambda: ' '.join(
                    widget.defaultHtmlClass + self.classes['field-error'])
            else:
                widget.htmlClass = lambda: ' '.join(
                    widget.defaultHtmlClass + self.classes['field'])

        for widget in self.actionWidgets:
            cls = self.classes['button']
            if widget.identifier in self.classes:
                cls = '{} {}'.format(cls, self.classes[widget.identifier])
            else:
                cls = f'{cls} btn-primary'
            widget.htmlClass = lambda: cls

    def application_url(self, name=None, data={}):
        """Return the URL of the nearest enclosing `grok.Application`.
        """
        return url(self.request, getApplication(), name=name, data=data)

    def flash(self, message, type='message'):
        """Send a short message to the user.
        """
        grokcore.message.send(message, type=type, name='session')


class EditForm(Form):
    grok.baseclass()
    grok.name('edit')
    grok.title(u"Edit")

    label = ""
    ignoreContent = False
    ignoreRequest = False
    actions = Actions(UpdateAction(("Update")),
                      CancelAction(("Cancel")))
    

class DefaultView(Form):
    grok.baseclass()
    mode = DISPLAY
    template = ChameleonPageTemplateFile("templates/display.cpt")
    ignoreRequest = True
    ignoreContent = False

    @property
    def label(self):
        dc = IDCDescriptiveProperties(self.context, None)
        if dc is not None and dc.title:
            return dc.title
        return getattr(self.context, '__name__', u'')
    
    def update(self):
        super().update()
        for widget in self.fieldWidgets:
            widget.defaultHtmlClass.append('form-control-plaintext')


Display = DefaultView

            
class AddForm(Form):
    grok.baseclass()
    _finishedAdd = False

    @base.action(u'Speichern', identifier="uvcsite.add")
    def handleAdd(self):
        data, errors = self.extractData()
        if errors:
            self.flash('Es sind Fehler aufgetreten')
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            #grok.notify(AfterSaveEvent(obj, self.request))

    def createAndAdd(self, data):
        obj = self.create(data)
        grok.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.add(obj)
        return obj

    def create(self, data):
        raise NotImplementedError

    def add(self, object):
        raise NotImplementedError

    def nextURL(self):
        raise NotImplementedError

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(AddForm, self).render()


@implementer(IGrokView)
class GrokView(ViewSupportMixin):
    pass


class View(BaseView):
    baseclass()


class Page(GrokView, BasePage):
    baseclass()


class TablePage(GrokView, TablePage):
    baseclass()
