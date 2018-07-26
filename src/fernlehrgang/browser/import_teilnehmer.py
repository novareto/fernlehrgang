# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
import os
from z3c import saconfig
from zope import component
from dolmen import menu
from grokcore import layout
from sqlalchemy import func, and_
from fernlehrgang import models
from uvc.layout import Page
from grokcore.chameleon.components import ChameleonPageTemplateFile as PageTemplate

from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import lieferstopps
from fernlehrgang.viewlets import NavigationMenu
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from fernlehrgang.browser.ergebnisse import CalculateResults
from fernlehrgang.exports.statusliste import getXLSBases, nN, un_helper, ges_helper


grok.templatedir('templates')


def createStatusliste(data):
    rcc = []
    for teilnehmer, unternehmen, ktn in data:
        #cal_res = CalculateResults(ktn)
        unternehmen = unternehmen[0]
        summary = ktn.result # cal_res.summary(lehrhefte)
        liste = []
        teilnehmer = ktn.teilnehmer
        ss = set([x.rlhid for x in ktn.antworten])
        antworten = len(ss)
        if teilnehmer:
            gebdat = ""
            if teilnehmer.geburtsdatum:
                try:
                    gebdat = teilnehmer.geburtsdatum.strftime('%d.%m.%Y')
                except:
                    gebdat = ""
            #unternehmen = teilnehmer.unternehmen
            liste.append(nN(teilnehmer.id))
            liste.append(nN(teilnehmer.titel))
            liste.append(nN(teilnehmer.anrede))
            liste.append(nN(teilnehmer.name))
            liste.append(nN(teilnehmer.vorname))
            liste.append(gebdat)
            liste.append(nN(teilnehmer.strasse))
            liste.append(nN(teilnehmer.nr))
            liste.append(nN(teilnehmer.plz))
            liste.append(nN(teilnehmer.ort))
            liste.append(nN(unternehmen.mnr))
            liste.append(nN(unternehmen.name))
            liste.append(nN(unternehmen.name2))
            liste.append(nN(unternehmen.name3))
            liste.append(nN(unternehmen.str))
            liste.append(nN(unternehmen.plz))
            liste.append(nN(unternehmen.ort))
            if teilnehmer.name:
                liste.append('ja')
            else:
                liste.append('nein')
            liste.append(nN(teilnehmer.kategorie))
            liste.append(nN(ktn.status))
            liste.append(un_helper(ktn.un_klasse))
            liste.append(nN(ktn.branche))
            liste.append(ges_helper(ktn.gespraech))
            liste.append(nN(summary['comment']))
            liste.append(nN(summary['resultpoints']))
            liste.append(nN(antworten))
        rcc.append(liste)
    book, adressen, rc = getXLSBases()
    r = rc + rcc
    print r
    for i, zeile in enumerate(r):
       adressen.append(zeile)
    fn = "/tmp/hans.xlsx"
    book.save(fn)
    return fn


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
        sql = session.query(models.Fernlehrgang).filter(models.Fernlehrgang.typ == self.context.typ)
        for flg in sql.all():
            rc.append(
                dict(
                    tn=len(flg.kursteilnehmer),
                    key=flg.id,
                    description=flg.beschreibung,
                    value="%s %s " % (flg.titel, flg.jahr))
            )
        return rc

    def render(self):
        filename = os.path.join(os.path.dirname(__file__),
                                'templates', 'import_teilnehmer.cpt')
        template = PageTemplate(filename)
        return template.render(self)

    def __call__(self):
        self.update()
        key = None
        for k, v in self.request.form.items():
            if k.startswith('import_'):
                key = k.replace('import_', '')
                action = "import"
            elif k.startswith('statusliste_'):
                key = k.replace('statusliste_', '')
                action = "statusliste"

        if not key:
            return Page.__call__(self)

        session = saconfig.Session()
        flg = session.query(models.Fernlehrgang).get(int(key))
        tids = [x.teilnehmer_id for x in self.context.kursteilnehmer]
        flgids = [x[0] for x in  session.query(models.Fernlehrgang.id).filter(models.Fernlehrgang.typ == self.context.typ).all() if x[0] != int(key) and x[0] != self.context.id]

        def check(ktn):
            if ktn.fernlehrgang_id in flgids:
                return False
            if ktn.teilnehmer.id in tids:
                return False
            if not 'Bestanden' in ktn.result['comment']:
                return False
            if ktn.status != 'A1':
                return False
            return True

        i = 0
        if action == "import":
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
        elif action == "statusliste":
            rc = []
            for ktn in flg.kursteilnehmer[:10]:
                if check(ktn):
                    rc.append((ktn.teilnehmer, ktn.teilnehmer.unternehmen, ktn))
            fn = createStatusliste(rc)
            self.request.response.setHeader(
                'content-disposition',
                'attachment; filename=%s' % 'Statusliste.xlsx')
            self.request.response.setHeader(
                'content-type',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            with open(fn, 'rb') as xlsx:
                return xlsx.read()
        #self.flash('Es wurden %s Teilnehmer erfolgreich registriert.' % i)
        return Page.__call__(self)
