# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok

from z3c import saconfig
from zope import component
from dolmen import menu
from grokcore import layout
from sqlalchemy import func, and_
from fernlehrgang import models
from uvc.layout import Page


from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import lieferstopps
from fernlehrgang.viewlets import NavigationMenu
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from zope.pluggableauth.interfaces import IAuthenticatorPlugin


grok.templatedir('templates')


@menu.menuentry(NavigationMenu, order=300)
class ImportTeilnehmer(Page):
    grok.context(IFernlehrgang)
    grok.title(u"Import Teilnehmer")

    title = u"Import Teilnehmer"

    @property
    def description(self):
        return u"Hier Sie verschiedene Statstiken zum Fernlehrgang '%s' aufrufen" % self.context.titel

    def getFernlehrgaenge(self):
        rc = []
        session = saconfig.Session()
        sql = session.query(models.Fernlehrgang)
        for flg in sql.all():
            rc.append(
                dict(tn=len(flg.kursteilnehmer), key=flg.id, value="%s %s " % (flg.titel, flg.jahr))
            )
        return rc

    def update(self):
        key = None
        for k, v in self.request.form.items():
            if k.startswith('import_'):
                key = k.replace('import_', '')

        if not key:
            return

        session = saconfig.Session()
        flg = session.query(models.Fernlehrgang).get(key)

        def check(ktn):
            return True

        i = 0
        for ktn in flg.kursteilnehmer:
            if check(ktn):
                ktnn = models.Kursteilnehmer(
                        status = ktn.status,
                        gespraech = ktn.gespraech,
                        un_klasse = ktn.un_klasse,
                        branche = ktn.branche,
                        teilnehmer_id = ktn.teilnehmer_id,
                        unternehmen_mnr = ktn.unternehmen_mnr
                    )
                self.context.kursteilnehmer.append(ktnn)
                i += 1
        self.flash('Es wurden %s Teilnehmer erfolgreich registriert.' % i)
