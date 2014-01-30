# -*- coding: utf-8 -*-

import grok
from megrok.layout import Page


grok.templatedir('templates')


class NotFound(Page, grok.components.NotFoundView):
    """Not Found Error View
    """
    pass


class SystemError(Page, grok.components.ExceptionView):
    """Custom System Error for UVCSITE
    """

    def __init__(self, context, request):
        super(SystemError, self).__init__(context, request)
        self.context = grok.getSite()
        self.origin_context = context
