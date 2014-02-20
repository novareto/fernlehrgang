# -*- coding: utf-8 -*-

import grok
import uvc.layout
from zope.interface import Interface 
from dolmen.app.container import AddMenu
from .skin import IQuestionary
from ..interfaces import IMembership


grok.templatedir('templates')


class ContainerMenu(AddMenu):
    grok.viewletmanager(uvc.layout.interfaces.IAboveContent)
    grok.view(Interface)
    grok.layer(IQuestionary)


class MemberData(uvc.layout.MenuItem):
    grok.context(Interface)
    grok.title(u"Registrierdaten")
    grok.viewletmanager(uvc.layout.IPersonalPreferences)
    grok.require('zope.View')
    grok.layer(IQuestionary)

    @property
    def action(self):
        return "%s/member/%s" % (
            self.view.application_url(), self.view.request.principal.id)


class MemberCourses(grok.Viewlet):
    grok.viewletmanager(uvc.layout.IPageTop)
    grok.context(Interface)
    grok.order(30)
    grok.require('zope.View')
    grok.layer(IQuestionary)

    def update(self):
        membership = IMembership(self.request.principal, None)
        if membership is None:
            self.courses = None
        else:
            url = self.view.application_url()
            self.courses = [{"url": '%s/course/%s' % (url, c.id),
                             "title": c.titel} for c in membership.courses]


class MemberContact(grok.Viewlet):
    grok.viewletmanager(uvc.layout.IPageTop)
    grok.context(Interface)
    grok.order(40)
    grok.require('zope.View')
    grok.layer(IQuestionary)
