# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

from zope import component, interface, schema


class IAddUserForm(interface.Interface):

    login = schema.BytesLine(
        title = u'Anmeldename',
        description = u"Bitte geben Sie hier den Anmeldenamen ein.",  
        required = True
        )

    email = schema.BytesLine(
        title = u'EMail Adresse',
        description = u"Bitte geben Sie hier die EMail Adresse des Benutzers ein.",  
        required = True
        )

    password = schema.Password(
        title = u'Passwort', 
        description = u"Bitte tragen Sie hier das Passwort ein.",  
        required = True
        )

    confirm_password = schema.Password(
        title = u'Passwort bestätigen', 
        description = u"Bitte wiederholen Sie aus Sicherheitsgründen das Passwort.",  
        required=True
        )

    real_name = schema.BytesLine(
        title=u'Vollständiger Name',
        description = u"Bitte geben Sie den vollständigen Namen ein.", 
        required=True
        )

    role = schema.Choice(
        title=u'Rolle',
        description = u"Bitte wählen Sie eine Rolle für den Benuzter aus.",
        values=('FIXME',),
        required=True
        )
