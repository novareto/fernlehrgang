# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import grokcore.component as grok
from zope import interface, schema
from zope.schema.interfaces import IContextSourceBinder


VOCABULARY = None


@grok.provider(IContextSourceBinder)
def getTeilnehmerId(context):
    return VOCABULARY


class ISearch(interface.Interface):
    id = schema.TextLine(
        title="Teilnehmer ID",
    )
