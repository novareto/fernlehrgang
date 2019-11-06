# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import grok

from megrok.pagetemplate import PageTemplate
from .interfaces import (
    IGlobalMenu,
    IPersonalPreferences,
    IDocumentActions,
    IExtraViews,
    ISpotMenu,
    IPersonalMenu,
    IQuickLinks,
    IFooter,
)
from zope.component import getMultiAdapter
from zope.interface import Interface, implementer
from zope.pagetemplate.interfaces import IPageTemplate
from uvc.menus.components import MenuRenderer, Menu, IMenu


grok.templatedir("templates")


@implementer(IGlobalMenu)
class GlobalMenu(Menu):
    grok.name("globalmenu")


@implementer(IFooter)
class FooterMenu(Menu):
    grok.name("footermenu")


@implementer(IPersonalPreferences)
class PersonalPreferences(Menu):
    grok.name("personalpreferences")


@implementer(IDocumentActions)
class DocumentActionsMenu(Menu):
    grok.name("documentactions")


@implementer(IExtraViews)
class ExtraViews(Menu):
    grok.name("extraviews")


@implementer(ISpotMenu)
class SpotMenu(Menu):
    grok.name("spotmenu")


@implementer(IPersonalMenu)
class PersonalMenu(Menu):
    grok.name("personal_menu")


@implementer(IQuickLinks)
class QuickLinks(Menu):
    grok.name("quicklinks")


class PersonalMenuRenderer(MenuRenderer):
    grok.context(Interface)
    grok.name("personalmenu")

    bound_menus = ('personal_menu', )


class GlobalMenuRenderer(MenuRenderer):
    grok.context(Interface)
    grok.name("globalmenu")

    bound_menus = ("globalmenu",)


class FooterMenuRenderer(MenuRenderer):
    grok.context(Interface)
    grok.name("footer")

    bound_menus = ("footermenu",)
