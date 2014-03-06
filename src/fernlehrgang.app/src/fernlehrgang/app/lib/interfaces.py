# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grokcore.component as grok

from zope.schema.interfaces import IVocabularyFactory, IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema import TextLine, Choice, List, Date, Set
from zope.interface import Interface
from fernlehrgang import models
from cromlech.sqlalchemy import get_session


@grok.provider(IContextSourceBinder)
def flgs(context):
    session = get_session('fernlehrgang')
    rc = []
    for flg in session.query(models.Fernlehrgang):
        if len(flg.lehrhefte) == 1:
            rc.append(SimpleTerm(flg.id, flg.id, flg.titel))
    return SimpleVocabulary(rc)



@grok.provider(IContextSourceBinder)
def lehrhefte(context):
    rc = []
    for lehrheft in context.lehrhefte:
        titel = "%s, %s" %(lehrheft.nummer, lehrheft.titel)
        key = "%s-%s" %(lehrheft.id, lehrheft.nummer)
        rc.append(SimpleTerm(key, key, titel))
    return SimpleVocabulary(rc)


class IXLSReport(Interface):
        """ xls report """


class IXLSExport(Interface):
    """ xml export """

    dateiname = TextLine(
        title=u"Dateiname",
        description=u"Dateiname"
        )

    rdatum = TextLine(
        title=u"RDatum",
        description=u"RDatum"
        )

    stichtag = TextLine(
        title=u"Stichtag",
        description=u"Stichtag"
        )

    lehrheft = Choice(
        title=u"Lehrheft",
        description=u"Lehrheft",
        source = lehrhefte,
        )


    def createXLS():
        """ """

class IXLSFortbildung(Interface):

    fortbildungen = Set(
        title=u"Fortbildungen",
        description=u"Bitte wählen sie die Fortbildungen die berücksichtigt werden sollen",
        value_type=Choice(source = flgs),
        )

    stichtag = Date(
        title=u"Stichtag",
        description=u"Anworten ab letztem Versandtag (inklusive)."
        )
