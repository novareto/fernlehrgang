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

    name2 = TextLine(
        title = u'Name2',
        description = u'Name des Unternehmens',
        required = True
        )

    name3 = TextLine(
        title = u'Name3',
        description = u'Name des Unternehmens',
        required = True
        )

    str = TextLine(
        title = u'Strasse',
        description = u'Strasse des Unternehmens',
        required = True
        )

    plz = TextLine(
        title = u'Postleitzahl',
        description = u'Postleitzahl des Unternehmens',
        required = True
        )

    ort = TextLine(
        title = u'Ort',
        description = u'Ort des Unternehmens',
        required = True
        )

