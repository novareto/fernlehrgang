# package

from grok.components import ViewSupportMixin
from grok import baseclass, View as BaseView
from grok.interfaces import IGrokView
from grokcore.layout import Page as BasePage
from megrok.z3ctable import TablePage
from zope.interface import implementer


@implementer(IGrokView)
class GrokView(ViewSupportMixin):
    pass


class View(BaseView):
    baseclass()


class Page(GrokView, BasePage):
    baseclass()


class TablePage(GrokView, TablePage):
    baseclass()
