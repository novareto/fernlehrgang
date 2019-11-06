# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

from zope import interface, schema
class ISearch(interface.Interface):

    id = schema.TextLine(
        title=u"Teilnehmer ID",
        )
