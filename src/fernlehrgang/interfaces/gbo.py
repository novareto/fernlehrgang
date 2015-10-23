# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

from zope.interface import Interface
from zope.schema import Choice
from .kursteilnehmer import janein, un_klasse, gespraech


class IGBOData(Interface):

    un_klasse = Choice(
        title=u"Mitarbeiteranzahl",
        description=u'Hier können Sie die Gruppe des Unternehmens festlegen.',
        required=False,
        source=un_klasse,
        )

    branche = Choice(
        title=u"Branche",
        description=u'Betrieb ist ein Recyclingunternehmen, ein Motorradhandel\
                oder ein Speditions- oder Umschalgunternehmen.',
        required=True,
        source=janein,
        default='nein',
        )
