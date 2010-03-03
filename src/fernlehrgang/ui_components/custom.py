# -*- coding: utf-8 -*-

import megrok.pagetemplate as pt
from dolmen.app.layout.models import DefaultView


class DisplayTemplate(pt.PageTemplate):
    """The basic template for a display form.
    """
    pt.view(DefaultView)
