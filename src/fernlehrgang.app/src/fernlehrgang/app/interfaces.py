# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grokcore.component as grok

from cromlech.sqlalchemy import get_session
from fernlehrgang.models import *
from fernlehrgang.models.vocabularies import register_vocabulary
from uvc.themes.dguv import IDGUVRequest
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class IFernlehrgangSkin(IDGUVRequest):
    pass


class IListing(Interface):
    """ Marker for Listings.
    """


class IFernlehrgangApp(Interface):
    """ Marker Interface für den Fernlehrgang.
    """


@grok.provider(IContextSourceBinder)
def lehrheft_vocab(context):    
    rc = [SimpleTerm(0, 'Bitte eine Auswahl treffen',
                     'Bitte eine Auswahl treffen')]
    if IAntwort.providedBy(context):
        fernlehrgang = context.kursteilnehmer.fernlehrgang
    if IKursteilnehmer.providedBy(context):
        fernlehrgang = context.fernlehrgang
    for lehrheft in fernlehrgang.lehrhefte:
        value = "%s - %s" % (lehrheft.nummer, lehrheft.titel)
        rc.append(SimpleTerm(lehrheft.id, lehrheft.id, value))
    return SimpleVocabulary(rc)


@grok.provider(IContextSourceBinder)
def fragen_vocab(context):
    rc = [SimpleTerm(0, 'Bitte eine Auswahl treffen',
                     'Bitte eine Auswahl treffen')]
    if IAntwort.providedBy(context):
        fernlehrgang = context.kursteilnehmer.fernlehrgang
    if IKursteilnehmer.providedBy(context):
        fernlehrgang = context.fernlehrgang
    for lehrheft in fernlehrgang.lehrhefte:
        for frage in lehrheft.fragen: 
            term = "%s - %s" %(frage.frage, frage.titel)
            rc.append(SimpleTerm(frage.id, frage.id, term))           
    return SimpleVocabulary(sorted(rc, key=lambda term: term.value))


@grok.provider(IContextSourceBinder)
def fernlehrgang_vocab(context):
    rc = [SimpleTerm('', '', u'Fernlehrgang auswählen')]
    session = get_session('fernlehrgang')
    from fernlehrgang.models import Fernlehrgang
    sql = session.query(Fernlehrgang)

    def getKTN(context, flg_id):
        if IFernlehrgangApp.providedBy(context):
            return 
        if not hasattr(context, 'kursteilnehmer'):
            return True 
        for x in context.kursteilnehmer:
            if flg_id == x.fernlehrgang_id:
                return x

    for flg in sql.all():
        ktn = getKTN(context, flg.id)
        if ktn:
            value = "%s - %s, bereits Registriert" % (flg.titel, flg.jahr)
            if ktn is True:
                token = flg.id
            else:
                token = "%s,%s" %(ktn.id, flg.id)
            rc.append(SimpleTerm(token, token, value))
        else:
            value = "%s - %s" % (flg.titel, flg.jahr)
            rc.append(SimpleTerm(flg.id, flg.id, value))
    return SimpleVocabulary(rc) 


register_vocabulary(lehrheft_vocab, 'lehrheft')
register_vocabulary(fragen_vocab, 'fragen')
register_vocabulary(fernlehrgang_vocab, 'fernlehrgang')
