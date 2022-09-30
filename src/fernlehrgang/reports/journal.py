# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2013 NovaReto GmbH
# # cklinger@novareto.de

import grok

from fernlehrgang import models
from z3c.saconfig import Session
from megrok.traject import locate
from fernlehrgang.browser import Form
from fernlehrgang.viewlets import NavEntry
from megrok.traject.components import DefaultModel
from zeam.form.base import action, Fields, NO_VALUE
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.journal import IJournalEntry, get_status


grok.templatedir("templates")


source = get_status(None)


class ChangeWf(grok.View):
    grok.context(IFernlehrgangApp)

    def update(self):
        jid = str(self.request.form.get("jid"))
        session = Session()
        entry = session.query(models.JournalEntry).get(jid)
        entry.status = u"1000"

    def render(self):
        self.flash(u"Der Journal Eintrag wurde erfolgreich geändert!")
        status = self.request.form.get("form.field.status")
        url = "%s/journal_listing" % self.application_url()
        if status is not NO_VALUE:
            url = "%s?form.field.status=%s" % (url, status)
        self.redirect(url)


class SBNavEntry(NavEntry):
    grok.context(IFernlehrgangApp)
    grok.name('svnaventry')
    grok.require('zope.View')
    grok.order(30)

    title = u"Sachbearbeitung"
    icon = "fas fa-code-branch"

    def url(self):
        return self.view.url(self.context, 'journal_listing')


class JournalListing(Form):
    grok.context(IFernlehrgangApp)
    grok.name("journal_listing")
    grok.title(u"Sachbearbeitung")
    grok.order(30)

    ignoreRequest = False

    fields = Fields(IJournalEntry).select("status")

    label = u"Sachbearbeitung"
    description = u""

    def update(self):
        session = Session()
        if self.request.method == "POST":
            for jid in  self.request.form.get('ids', []):
                session.delete(session.query(models.JournalEntry).get(jid))
                self.flash('Eintrage %s entfernt!' % jid)
        session.flush()
        for field in self.fields:
            field.required = False
            field.readonly = False
        data, errors = self.extractData()
        status = data.get("status")
        if status is not NO_VALUE:
            status = [status]
        else:
            status = [u"4", u"409"]
        self.results = (
            session.query(models.JournalEntry)
            .filter(models.JournalEntry.status.in_(status))
            .order_by(models.JournalEntry.id.desc())
            .all()
        )

    def getStatus(self, v):
        return source.getTerm(v).title

    def getResults(self):
        for item in self.results:
            locate(grok.getSite(), item, DefaultModel)
            yield item

    def getAktionen(self, result):
        rc = []
        data, errors = self.extractData()
        base = self.application_url()
        href = "%s/changewf?jid=%s"
        if "status" in data.keys():
            href = "%s&form.field.status=%s" % (href, data["status"])
        if result.status in ["4", "409"]:
            rc.append(dict(href=href % (base, result.id), title=u"Löschen"))
        return rc

    @action(u"Suchen")
    def handle_search(self):
        self.flash(u"Ihre Suche wurde geändert")
