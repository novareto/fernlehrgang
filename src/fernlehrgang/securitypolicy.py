# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok


from zope.component import getUtilitiesFor
from zope.securitypolicy.interfaces import IRole
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory


class Roles(grok.GlobalUtility):
    grok.name('uvc.auth.roles')
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
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
    grok.name('uvc.bgeadminstrator')
    grok.title('BGHW Administrator')
    grok.permissions('uvc.managefernlehrgang', 
                     'dolmen.content.Edit',
                     'uvc.manageteilnehmer')

class DAABenutzer(grok.Role):
    grok.name('uvc.daabenutzer')
    grok.title('DAA Mitarbeiter')
    grok.permissions('uvc.manageteilnehmer',
                     'dolmen.content.Edit',)
