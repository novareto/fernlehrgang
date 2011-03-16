# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 NovaReto GmbH
# cklinger@novareto.de 

import grokcore.component as grok

from zope.schema import *
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder


@grok.provider(IContextSourceBinder)
def reduce_lehrheft(context):
    from fernlehrgang.interfaces.flg import IFernlehrgang
    rc = []
    reduce = []
    alle = range(1, 11)
    if ILehrheft.providedBy(context):
        lehrhefte = context.fernlehrgang.lehrhefte
    if IFernlehrgang.providedBy(context):
        lehrhefte = context.lehrhefte
        reduce = [int(x.nummer) for x in lehrhefte]
    for x in alle:
        if x not in reduce:
            rc.append(SimpleTerm(str(x), str(x), str(x)))
    return SimpleVocabulary(rc)   


class ILehrheft(Interface):

    id = Int(
        title = u'Id',
        description = u'Eindeutige Kennzeichnung des Fernlehrgangs',
        required = False,
        readonly = True
        )

    nummer = Choice(
        title = u'Nummer',
        description = u'Die Nummer des Lehrgangs. Diese sollte Fortlaufend 1-8 sein',
        required = True,
        source = reduce_lehrheft,
        )

    titel = TextLine(
        title = u'Titel',
        description = u'Titel des Lehrhefts.',
        required = True
        )
