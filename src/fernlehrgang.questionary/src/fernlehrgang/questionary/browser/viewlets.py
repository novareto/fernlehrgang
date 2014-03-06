# -*- coding: utf-8 -*-

import uvclight
from dolmen import menu
from uvclight.interfaces import IPageTop, IAboveContent, IPersonalPreferences
from zope.interface import Interface 
from ..interfaces import IMembership
from ..app import IQuizzSkin


class ContainerMenu(menu.Menu):
    uvclight.name('uvcsite-addmenu')
    uvclight.context(Interface)
    uvclight.title(u'Hinzufügen')
    uvclight.layer(IQuizzSkin)

    template = None

    menu_class = u'nav nav-pills'
    css = "addmenu"


class MemberData(uvclight.MenuItem):
    uvclight.context(Interface)
    uvclight.title(u"Registrierdaten")
    uvclight.menu(IPersonalPreferences)
    uvclight.require('zope.View')
    uvclight.layer(IQuizzSkin)

    @property
    def action(self):
        return "%s/member/%s" % (
            self.view.application_url(), self.view.request.principal.id)


class MemberCourses(uvclight.Viewlet):
    uvclight.viewletmanager(IPageTop)
    uvclight.context(Interface)
    uvclight.order(30)
    uvclight.require('zope.View')
    uvclight.layer(IQuizzSkin)

    template = uvclight.get_template('membercourses.cpt', __file__)
    
    def update(self):
        #membership = IMembership(self.request.principal, None)
        membership = None
        if membership is None:
            self.courses = None
        else:
            url = self.view.application_url()
            self.courses = [{"url": '%s/course/%s' % (url, c.id),
                             "title": c.titel} for c in membership.courses]


class MemberContact(uvclight.Viewlet):
    uvclight.viewletmanager(IPageTop)
    uvclight.context(Interface)
    uvclight.order(40)
    uvclight.require('zope.View')
    uvclight.layer(IQuizzSkin)

    template = uvclight.get_template('membercontact.cpt', __file__)
