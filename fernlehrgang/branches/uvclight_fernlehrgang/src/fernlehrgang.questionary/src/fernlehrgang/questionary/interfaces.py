# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import List, Object
from fernlehrgang.models import IFernlehrgang
from zope.security.interfaces import IPrincipal


class IQuizz(Interface):
    pass


class IMembership(Interface):
    """This component abstracts the membership to provide useable
    informations about the member and its participations.
    """
    courses = List(
        title=u"Member's courses",
        value_type=Object(schema=IFernlehrgang))
