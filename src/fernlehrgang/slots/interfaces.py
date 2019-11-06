import zope.interface


class IPageTop(zope.interface.Interface):
    """Marker For the area that sits at the top of the page.
    """


class ITabs(zope.interface.Interface):
    """Marker for the action tabs.
    """


class IAboveContent(zope.interface.Interface):
    """Marker For the area that sits above the page body.
    """


class IBelowContent(zope.interface.Interface):
    """Marker For the area that sits under the page body.
    """


class IHeaders(zope.interface.Interface):
    """Marker For Headers
    """


class IToolbar(zope.interface.Interface):
    """Marker for Toolbar
    """


class IFooter(zope.interface.Interface):
    """
    """


class IBeforeActions(zope.interface.Interface):
    """
    """


class IPersonalMenu(zope.interface.Interface):
    """
    """

    
class IExtraInfo(zope.interface.Interface):
    """
    """



class IPersonalPreferences(zope.interface.Interface):
    """Marker for PersonalPreferences
    """


class IGlobalMenu(zope.interface.Interface):
    """Marker for GlobalMenu
    """


class IPersonalMenu(zope.interface.Interface):
    """Marker for PersonalMenu
    """


class IDocumentActions(zope.interface.Interface):
    """Marker for DocumentActions
    """


class IQuickLinks(zope.interface.Interface):
    """Marker for Qucklinks
    """


class IExtraViews(zope.interface.Interface):
    """Marker for additional Views for Folders
       Objects etc...
    """

class ISpotMenu(zope.interface.Interface):
    """ Special Menu """


__all__ = [
    "IAboveContent",
    "IBeforeActions",
    "IBelowContent",
    "IExtraInfo",
    "IFooter",
    "IHeaders",
    "IPageTop",
    "IPersonalMenu",
    "ITabs",
    "IToolbar",
    ]
