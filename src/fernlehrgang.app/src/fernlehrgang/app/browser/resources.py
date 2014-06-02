# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import uvclight
from uvclight import interfaces

from dolmen.uploader.resources.hayageek import uploader as hayageek
from fanstatic import Library, Resource, Group
from js.jquery import jquery
from zope.interface import Interface
from uvc.js.wysiwyg import bs_wysihtml5


library = Library('fernlehrgang.app.browser', 'static')
js = Group([bs_wysihtml5])
register_js = Resource(library, 'register.js', depends=[jquery])
fernlehrgang_css = Resource(library, 'flg.css')
fernlehrgang_js = Resource(library, 'flg.js', depends=[jquery])

# Upload JS
upload = Resource(library, 'upload.js', depends=[hayageek], bottom=True)

cal_library = Library('Calendar', '3rdparty')
jstimezone = Resource(cal_library, 'jstz.js')
underscore = Resource(cal_library, 'underscore-min.js')
calendarcss =  Resource(cal_library, 'calendar.css')
calendar = Resource(cal_library, 'calendar.js',
                    depends=[jquery, jstimezone, underscore])

bs_calendar = Group([calendar, calendarcss])


class Resources(uvclight.Viewlet):
    uvclight.viewletmanager(interfaces.IHeaders)

    def render(self):
        js.need()
        fernlehrgang_css.need()
        fernlehrgang_js.need()
        return u''
