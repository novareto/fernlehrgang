# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2013 NovaReto GmbH
# # cklinger@novareto.de

import grok

from uvc.layout import Page
from fernlehrgang import Form
from fernlehrgang import models
from z3c.saconfig import Session
from megrok.traject import locate
from dolmen.menu import menuentry
from zeam.form.base import action, Fields
from fernlehrgang.viewlets import NavigationMenu
from megrok.traject.components import DefaultModel
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.journal import IJournalEntry, get_status


grok.templatedir('templates')


source = get_status(None)


class ChangeWf(grok.View):
    grok.context(IFernlehrgangApp)

    def update(self):
        jid = str(self.request.form.get('jid'))
        session = Session()
        entry = session.query(models.JournalEntry).get(jid)
        print "DO STUFF WITH %s" % entry

    def render(self):
        self.flash(u'Der Journal Eintrag wurde erfolgreich geändert!')
        self.redirect("%s/journal_listing" % self.application_url())


@menuentry(NavigationMenu)
class JournalListing(Form):
    grok.context(IFernlehrgangApp)
    grok.name('journal_listing')
    grok.title(u"Sachbearbeitung")
    grok.order(30)

    fields = Fields(IJournalEntry).select('status')

    label = u"Sachbearbeitung"
    description = u""

    def update(self):
        session = Session()
        self.results = session.query(models.JournalEntry).filter(models.JournalEntry.status.in_([u"4", u"409"])).all()
        for field in self.fields:
            field.required = False
            field.readonly = False

    def getStatus(self, v):
        return source.getTerm(v).title

    def getResults(self):
        for item in self.results:
            locate(grok.getSite(), item, DefaultModel)
            yield item

    def getAktionen(self, result):
        rc = []
        base = self.application_url()
        href = "%s/changewf?jid=%s"
        if result.status == "4":
            rc.append(
                dict(href=href % (base, result.id), title=u"Lösen")
            )
        return rc
 

    @action(u"Suchen")
    def handle_search(self):
        data, errors = self.extractData()
        session = Session()
        self.results = session.query(models.JournalEntry).filter(
                models.JournalEntry.status == data['status']).all()
