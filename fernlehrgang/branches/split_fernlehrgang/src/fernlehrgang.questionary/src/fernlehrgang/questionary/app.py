# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from zope.pluggableauth import PluggableAuthentication
from zope.authentication.interfaces import IAuthentication


def setup_pau(PAU):
    PAU.authenticatorPlugins = ('rdbauth', )
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")


class Questionaries(grok.Application, grok.Container):

    grok.local_utility(
        PluggableAuthentication, 
        provides=IAuthentication,
        public=True,
        setup=setup_pau,
        )
