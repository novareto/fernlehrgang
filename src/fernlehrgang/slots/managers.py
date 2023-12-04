import grok
import zope.interface
from fernlehrgang.slots import interfaces

grok.context(zope.interface.Interface)
grok.templatedir("templates")


class IHeader(zope.interface.Interface):
    pass


@zope.interface.implementer(interfaces.IHeaders)
class Headers(grok.ViewletManager):
    """Viewlet Manager for the Header"""

    grok.name("headers")

    def update(self):
        super().update()
        for viewlet in self.viewlets:
            if IHeader.providedBy(viewlet):
                viewlet.render()

    def render(self):
        results = (v.render() for v in self.viewlets if not IHeader.providedBy(v))
        return "\n".join([r for r in results if r.strip()])


@zope.interface.implementer(interfaces.ITabs)
class Tabs(grok.ViewletManager):
    grok.name("tabs")

    def content(self):
        results = [v.render() for v in self.viewlets]
        return "\n".join([r for r in results if r.strip()])

    def render(self):
        res = self.content()
        if not res:
            return ""
        return f"<ul class='nav justify-content-end'>{res}</ul>"


@zope.interface.implementer(interfaces.IAboveContent)
class AboveContent(grok.ViewletManager):
    grok.name("above-body")


@zope.interface.implementer(interfaces.IBelowContent)
class BelowContent(grok.ViewletManager):
    grok.name("below-body")


@zope.interface.implementer(interfaces.IPageTop)
class PageTop(grok.ViewletManager):
    grok.name("pagetop")


@zope.interface.implementer(interfaces.IFooter)
class Footer(grok.ViewletManager):
    grok.name("footer")
    grok.require("zope.View")


@zope.interface.implementer(interfaces.IBeforeActions)
class BeforeActions(grok.ViewletManager):
    grok.name("uvcsite.beforeactions")
    grok.require("zope.View")


@zope.interface.implementer(interfaces.IExtraInfo)
class ExtraInfo(grok.ViewletManager):
    grok.name("uvcsite.extrainfo")
    grok.require("zope.View")
