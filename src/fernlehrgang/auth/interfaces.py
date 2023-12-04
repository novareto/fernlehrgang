# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

from zope import interface, schema
from fernlehrgang.auth.securitypolicy import roles


class IAddUserForm(interface.Interface):
    login = schema.TextLine(
        title="Anmeldename",
        description="Bitte geben Sie hier den Anmeldenamen ein.",
        required=True,
    )

    email = schema.TextLine(
        title="EMail Adresse",
        description="Bitte geben Sie hier die EMail Adresse des Benutzers ein.",
        required=True,
    )

    password = schema.Password(
        title="Passwort",
        description="Bitte tragen Sie hier das Passwort ein.",
        required=True,
    )

    confirm_password = schema.Password(
        title="Passwort bestätigen",
        description="Bitte wiederholen Sie aus Sicherheitsgründen das Passwort.",
        required=True,
    )

    real_name = schema.TextLine(
        title="Vollständiger Name",
        description="Bitte geben Sie den vollständigen Namen ein.",
        required=True,
    )

    role = schema.Choice(
        title="Rolle",
        description="Bitte wählen Sie eine Rolle für den Benuzter aus.",
        source=roles,
        required=True,
    )
