# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface

class ITeilnehmer(Interface):

    id = TextLine(
        title = u'id',
        description = u'Eindeutige Id für den Teilnehmer',
        required = False,
        readonly = True
        )

    name = TextLine(
        title = u'Name',
        description = u'Name des Unternehmens',
        required = True
        )

