# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

from vocabs import roles, zuordnung, zuordnung_police
from zope import component, interface, schema

class IAddUserForm(interface.Interface):

    login = schema.BytesLine(
        title=u'Benutzername',
        description = u"Bitte geben Sie einen Benutzernamen ein z.b HMustermann",  
        required=True
        )

    password = schema.Password(
        title=u'Passwort', 
        required=True
        )

    confirm_password = schema.Password(
        title=u'Passwort bestaetigen', 
        required=True
        )

    real_name = schema.BytesLine(
        title=u'Vollstaendiger Name',
        description = u"Bitte geben Sie den vollstaendigen Namen ein z.b Heinz Mustermann", 
        required=True
        )

    role = schema.Choice(
        title=u'Benutzerrolle',
        description = u"Bitte waehlen Sie die richtige Rolle aus.",
        source=roles,
        required=True
        )
