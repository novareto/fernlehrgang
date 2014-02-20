# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import List, Object
from fernlehrgang.models import IFernlehrgang
from zope.security.interfaces import IPrincipal
from zope.pluggableauth.interfaces import IPrincipalInfo


class IMemberInfo(IPrincipalInfo):
    """This component is a specialisation of a common IPrincipalInfo.
    """

    
class IMember(IPrincipal):
    """This component is the representation of a fernlehrgang member.
    """


class IMembership(Interface):
    """This component abstracts the membership to provide useable
    informations about the member and its participations.
    """
    courses = List(
        title=u"Member's courses",
        value_type=Object(schema=IFernlehrgang))
