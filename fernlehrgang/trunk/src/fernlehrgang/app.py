import grok

class FernlehrgangApp(grok.Application, grok.Container):
    pass

class Index(grok.View):
    pass # see app_templates/index.pt
