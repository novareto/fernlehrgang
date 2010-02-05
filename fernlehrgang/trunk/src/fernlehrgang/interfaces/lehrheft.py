# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface

class ILehrheft(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des Fernlehrgangs',
        required = False,
        readonly = True
        )

    nummer = Int(
        title = u'Nummer',
        description = u'Die Nummer des Lehrgangs. Diese sollte Fortlaufend 1-8 sein',
        required = True,
        )

    titel = TextLine(
        title = u'Titel',
        description = u'Titel des Lehrhefts.',
        required = True
        )
