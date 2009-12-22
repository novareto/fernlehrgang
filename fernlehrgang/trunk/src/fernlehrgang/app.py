import grok

class Fernlehrgang(grok.Application, grok.Container):
    pass

class Index(grok.View):
    pass # see app_templates/index.pt
