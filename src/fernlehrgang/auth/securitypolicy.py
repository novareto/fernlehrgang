# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import zope.security

from zope import interface
from grokcore.component import provider
from zope.component import getUtilitiesFor
from zope.securitypolicy.interfaces import IRole
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder


from zope.securitypolicy.interfaces import Allow
from zope.securitypolicy.securitymap import SecurityMap
from zope.securitypolicy.interfaces import IPrincipalRoleManager, IPrincipalRoleMap


def getRequest():
    return zope.security.management.getInteraction().participations[0]


@interface.implementer(IPrincipalRoleManager, IPrincipalRoleMap)
class FLGRolePermissionManager(SecurityMap, grok.Adapter):
    grok.context(interface.Interface)
    grok.provides(IPrincipalRoleManager)

    def __init__(self, context):
        super(FLGRolePermissionManager)
        esm = self._compute_extra_data()
        self._bycol = esm._bycol
        self._byrow = esm._byrow

    def _compute_extra_data(self):
        request = getRequest()
        principal = request.principal
        extra_map = SecurityMap()
        extra_map.addCell(principal.description, principal.id, Allow)
        return extra_map

    def getPrincipalsAndRoles(self):
        return self.getAllCells()

    def getPrincipalsForRole(self, rowentry):
        return self.getRow(rowentry)

    def getRolesForPrincipal(self, colentry):
        return self.getCol(colentry)

    def getSetting(self, rowentry, colentry, default=None):
        return self.queryCell(rowentry, colentry, default=None)


@provider(IContextSourceBinder)
def roles(context):
    items = []
    for name, utility in getUtilitiesFor(IRole, context):
        if name.startswith("uvc"):
            items.append((name, name, grok.title.bind().get(utility)))
    return SimpleVocabulary.fromItems(items)


class ManageFernlehrgang(grok.Permission):
    grok.name("uvc.managefernlehrgang")


class ManageTeilnehmer(grok.Permission):
    grok.name("uvc.manageteilnehmer")


class BGEAdminstrator(grok.Role):
    grok.name("uvc.bgeadministrator")
    grok.title("Administrator - Fernlehrgang")
    grok.permissions(
        "uvc.managefernlehrgang",
        "dolmen.content.Edit",
        "dolmen.content.Add",
        "dolmen.content.View",
        "zope.View",
        "uvc.manageteilnehmer",
    )


class BGHWReader(grok.Role):
    grok.name("uvc.reader")
    grok.title("Leser")
    grok.permissions(
        "dolmen.content.View",
        "zope.View",
    )
