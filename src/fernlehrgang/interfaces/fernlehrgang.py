# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface

class IFernlehrgang(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des Fernlehrgangs',
        required = False,
        readonly = True
        )

    jahr = Int(
        title = u'Jahr',
        description = u'Das Jahr in dem der Fernlehrgang stattfindent',
        required = True
        )

    titel = TextLine(
        title = u'Titel',
        description = u'Titel des Fernlehrgangs',
        required = True
        )

    beschreibung = Text(
        title = u'Beschreibung',
        description = u'Beschreibung des Fernlehrgangs',
        required = True
        )

    beginn = TextLine(title = u'Start',
        description = u'Zu welchen Datum soll der Fernlehrgang beginnen?',
        required = True
        )

    ende = TextLine(title = u'Ende',
        description = u'Zu welchen Datum soll der Fernlehrgang enden?',
        required = True
        )
