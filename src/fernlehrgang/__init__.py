# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
import logging
import grokcore.message
from grok import url
from grok import getApplication
from grokcore.layout.components import LayoutAware


from zeam.form.layout import Form
from zeam.form import base
from zeam.form.ztk.widgets.date import DateField
from megrok.z3ctable import TablePage

DateField.valueLength = "medium"


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


class Edit(Form):
    grok.baseclass()

class DefaultView(Form):
    grok.baseclass()

import zope.lifecycleevent

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


from zeam.form.base import DISPLAY
class Display(Form):
    grok.baseclass()
    grok.title(u"View")
    title=u""

    mode = DISPLAY
    ignoreRequest = True
    ignoreContent = False

    @property
    def label(self):
        dc = IDCDescriptiveProperties(self.context, None)
        if dc is not None and dc.title:
            return dc.title
        return getattr(self.context, '__name__', u'')




logger = logging.getLogger('fernlehrgang')

def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)

# SQLAlchemy LOGGING --> INFO for echo=True
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


def fmtDate(d):
    return "%02d.%02d.%02d" % (d.day, d.month, d.year)



from ibm_db_sa.base import DB2Compiler

def visit_sequence(self, sequence):
    nn = sequence.name
    if sequence.metadata.schema:
        nn = "%s.%s" %(sequence.metadata.schema, nn)
    return "NEXT VALUE FOR %s" % nn


DB2Compiler.visit_sequence = visit_sequence 
