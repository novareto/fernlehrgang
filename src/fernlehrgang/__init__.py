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
from zeam.form.ztk.widgets.date import DateField

DateField.valueLength = "medium"


class Form(Form, LayoutAware):
    grok.require('dolmen.content.Add')
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

class DefaultView(Form):
    grok.baseclass()

class AddForm(Form):
    grok.require('dolmen.content.Add')
    grok.baseclass()


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
