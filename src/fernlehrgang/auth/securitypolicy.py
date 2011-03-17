# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from grokcore.component import provider
from zope.component import getUtilitiesFor
from zope.securitypolicy.interfaces import IRole
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder


@provider(IContextSourceBinder)
def roles(context):
    items = []
    for name, utility in getUtilitiesFor(IRole, context):
        if name.startswith('uvc'):
            items.append((grok.title.bind().get(utility), name))
    return SimpleVocabulary.fromItems(items)


class ManageFernlehrgang(grok.Permission):
    grok.name('uvc.managefernlehrgang')

class ManageTeilnehmer(grok.Permission):
    grok.name('uvc.manageteilnehmer')


class BGEAdminstrator(grok.Role):
    grok.name('uvc.bgeadministrator')
    grok.title('Administrator - Fernlehrgang')
    grok.permissions('uvc.managefernlehrgang', 
                     'dolmen.content.Edit',
                     'dolmen.content.View',
                     'zope.View',
                     'uvc.manageteilnehmer')

