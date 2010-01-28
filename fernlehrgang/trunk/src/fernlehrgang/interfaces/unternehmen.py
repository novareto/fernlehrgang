# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grok

from zope.schema import *
from zope.interface import Interface

class IUnternehmen(Interface):

    mnr = TextLine(
        title = u'mnr',
        description = u'Mitgliedsnummer des Unternehmens',
        required = False,
        readonly = True
        )

    name = TextLine(
        title = u'Name',
        description = u'Name des Unternehmens',
        required = True
        )

