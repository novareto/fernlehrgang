# -*- coding: utf-8 -*-

import grok
from uvc.tbskin.skin import ITBSkin
from zope.interface import implementsOnly
from zope.publisher.browser import applySkin
from ..app import Questionaries
from grokcore.traverser import Traverser
from zope.publisher.interfaces.http import IHTTPRequest


class IQuestionary(ITBSkin):
    grok.skin('questionary')


@grok.subscribe(Questionaries, grok.IBeforeTraverseEvent)
def handle(obj, event):
    applySkin(event.request, IQuestionary)
