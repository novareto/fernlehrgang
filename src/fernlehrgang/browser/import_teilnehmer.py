# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import os
import grok
import datetime

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
from fernlehrgang.browser.ergebnisse import ICalculateResults
from fernlehrgang.exports.statusliste import getXLSBases, nN, un_helper, ges_helper
from fernlehrgang.exports.utils import page_query, makeZipFile, getUserEmail
from fernlehrgang.lib.emailer import send_mail
from fernlehrgang.exports import q
from sqlalchemy.orm import joinedload


grok.templatedir('templates')


def createStatusliste(data, flg_id):
    rcc = []
    i=1
    for teilnehmer, unternehmen, ktn, check in data:
        cal_res = ICalculateResults(ktn)
        i += 1
        print "CREATE STATUSLISTE"
        print i
        unternehmen = unternehmen
        summary = cal_res.summary()
        liste = []
        teilnehmer = ktn.teilnehmer
        #ss = set([x.rlhid for x in ktn.antworten])
        #antworten = len(ss)
        antworten = "N/A"
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
            liste.append(nN(teilnehmer.email))
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
            liste.append(check)
        rcc.append(liste)
    book, adressen, rc = getXLSBases()
    rc[0].append('CHECK')
    r = rc + rcc
    for i, zeile in enumerate(r):
       try:
           adressen.append(zeile)
       except:
           continue
    fn = "/tmp/hans.xlsx"
    fn = "/tmp/Vorschau_Import_%s.xlsx" % flg_id
    book.save(fn)
    return fn


def check(ktn, tids, flgids, aktiv):
    r = "OK, Teilnher kann importiert werden"
    if not aktiv:
         r = "Unternehmen des Teilnehmers nicht mehr aktiv"
    if ktn.fernlehrgang_id in flgids:
         r = "Teilnehmer bereits vorhanden"
         #return False
    if ktn.teilnehmer.id in tids:
        r = "Teilnehmer ist in registrierrt < 5 Jahre"
        #return False
    if 'Nicht Bestanden' in ktn.result['comment']:
        r = "Teilnehmer hat nicht bestanden"
        #return False
    if ktn.status not in ('A1', 'A2'): 
        r = "Teilnehmer Status nicht A1 o A2"
        #return False
    return r


def createXLS(mail, flg_id, tids, flgids):
    from z3c.saconfig import Session
    session = Session()
    flg = session.query(models.Fernlehrgang).get(int(flg_id))
    rc = []
    i = 0
    result = session.query(models.Teilnehmer, models.Unternehmen, models.Kursteilnehmer).options(joinedload(models.Kursteilnehmer.antworten)).filter(
        models.Kursteilnehmer.fernlehrgang_id == flg_id,
        models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
        models.Teilnehmer.unternehmen_mnr == models.Unternehmen.mnr).order_by(models.Teilnehmer.id)
    print result.count()
    for tn, unternehmen, ktn in page_query(result):
        print i
        i += 1
	#if check(ktn, tids, flgids):
	#    rc.append((ktn.teilnehmer, ktn.teilnehmer.unternehmen, ktn))
	rc.append((tn, unternehmen, ktn, check(ktn, tids, flgids, unternehmen.aktiv)))
    fn = createStatusliste(rc, flg_id)
    import transaction
    with transaction.manager:
        print "MAIL RAUS"
        send_mail('flgapp@bghw.de', (mail,), "Vorschau", "Vorschau", [fn,])


def importUsers(mail, flg_id, tids, flgids, context_id):
    from z3c.saconfig import Session
    import transaction
    with transaction.manager:
        session = Session()
        flg = session.query(models.Fernlehrgang).get(int(context_id))
        print flg
        rc = []
        i = 0
        y = 0
        result = session.query(models.Kursteilnehmer).filter(
            models.Kursteilnehmer.fernlehrgang_id == flg_id)
        alle = result.count()
        for ktn in result:
            print "%s von %s" % (y, alle)
            
            cc = check(ktn, tids, flgids, ktn.teilnehmer.unternehmen[0].aktiv)
   	    if cc == "OK, Teilnher kann importiert werden":
	        ktnn = models.Kursteilnehmer(
		        status = ktn.status,
		        gespraech = ktn.gespraech,
		        un_klasse = ktn.un_klasse,
		        branche = ktn.branche,
		        teilnehmer_id = ktn.teilnehmer_id,
		        unternehmen_mnr = ktn.unternehmen_mnr
		    )
	        flg.kursteilnehmer.append(ktnn)
	        i += 1
            y += 1
        print "MAIL RAUS"
        send_mail('flgapp@bghw.de', (mail,), "Import Erfolgreich", "Import Erfolgreich %s Teilnehmer importiert, Von %s  --> Nach %s" %(i, flg_id, context_id))

@menu.menuentry(NavigationMenu, order=300)
class ImportTeilnehmer(Page):
    grok.context(IFernlehrgang)
    grok.title(u"Import Teilnehmer")

    title = u"Import Teilnehmer"

    @property
    def description(self):
        return u"für Fernlehrgang %s (%s)" %(self.context.titel, self.context.id)

    def getFernlehrgaenge(self):
        rc = []
        session = saconfig.Session()
        sql = session.query(models.Fernlehrgang).filter(
            models.Fernlehrgang.jahr < int(datetime.datetime.now().strftime('%Y')) - 4
        )
        for flg in sql.all():
            rc.append(
                dict(
                    tn='XX',#len(flg.kursteilnehmer),
                    key=flg.id,
                    jahr=flg.jahr,
                    description=flg.beschreibung,
                    value="%s #(%s)" % (flg.titel, flg.id))
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

        #def check(ktn):
        #    if ktn.fernlehrgang_id in flgids:
        #        print "Teilnehmer in anderen FERNLEHRGANG"
        #        return False
        #    if ktn.teilnehmer.id in tids:
        #        print "Teilnehmer bereits in diesem FERNLEHRGANG"
        #        return False
        #    
        #    if 'Nicht Bestanden' in ktn.result['comment']:
        #        print "TEILNEHMER NICHT BESTANDEN"
        #        return False
        #    if ktn.status != 'A1':
        #        print "FALSCHER STATUS"
        #        return False
        #    return True

        i = 0
        if action == "import":
            mail = getUserEmail(self.request.principal.id)
            flg_id = flg.id
            #importUsers(mail, flg_id, tids, flgids)
            print "ADD STUFF TO THE QUEUEU"
            q.enqueue_call(func=importUsers, args=(mail, flg_id, tids, flgids, self.context.id), timeout=19800)
        elif action == "statusliste":
            mail = getUserEmail(self.request.principal.id)
            flg_id = flg.id
            #createXLS(mail, flg_id, tids, flgids)
            print "ADD STUFF TO THE QUEUEU"
            q.enqueue_call(func=createXLS, args=(mail, flg_id, tids, flgids), timeout=19800)

        #self.flash('Es wurden %s Teilnehmer erfolgreich registriert.' % i)
        return Page.__call__(self)
