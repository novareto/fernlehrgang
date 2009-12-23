import grok
from fernlehrgang.interfaces import IFernlehrgangApp

grok.templatedir('templates')

class FernlehrgangApp(grok.Application, grok.Container):
    grok.implements(IFernlehrgangApp) 

class Index(grok.View):
    pass # see app_templates/index.pt
