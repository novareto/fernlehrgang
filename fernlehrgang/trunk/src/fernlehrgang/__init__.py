import grok
from megrok.layout import Page as basePage

class Page(basePage, grok.View):
    grok.baseclass()
