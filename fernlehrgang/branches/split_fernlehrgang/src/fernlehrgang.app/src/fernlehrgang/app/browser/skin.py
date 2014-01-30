# -*- coding: utf-8 -*-

import grok
from uvc.tbskin.skin import ITBSkin
from zope.publisher.browser import applySkin
from .. import FernlehrgangApp


class RestLayer(grok.IRESTLayer):
    """ Layer for Rest Access"""
    grok.restskin('api')


class IFernlehrgangSkin(ITBSkin):
    grok.skin('fernlehrgang')


@grok.subscribe(FernlehrgangApp, grok.IBeforeTraverseEvent)
def handle(obj, event):
    applySkin(event.request, IFernlehrgangSkin)
