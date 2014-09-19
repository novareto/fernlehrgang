# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import grok

from dolmen.menu import menuentry
from fernlehrgang import models
from fernlehrgang.browser.ergebnisse import CalculateResults
from fernlehrgang.exports.menus import ExportItems
from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.lib import nN
from openpyxl.workbook import Workbook
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, joinedload
from fernlehrgang.interfaces.kursteilnehmer import un_klasse, gespraech
from fernlehrgang.exports.utils import page_query, makeZipFile, getUserEmail
from lxml.builder import E
from lxml import etree as ET



def createRows(session, flg_id):
    rc = []
    FERNLEHRGANG_ID = flg_id
    result = session.query(models.Teilnehmer)
    result = result.filter(
        and_(
            models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id,
            models.Kursteilnehmer.un_klasse == "G3",
            #models.Teilnehmer.kompetenzzentrum == "ja",
            )).order_by(models.Teilnehmer.id)
    i=1
    return result

def nN(v):
    if v:
        return v
    return ''


def export(session, flg_id):
    """This should be the "shared" export function.
    """
    fn = "/tmp/k_zentrum_%s.xml" % flg_id
    rc = createRows(session, flg_id)
    print rc.count()
    xml = E('Komptenzzentrum')
    i=1
    for teilnehmer in rc:
        i+=1
        if teilnehmer.kompetenzzentrum == "ja":
            lhg = E(u'Lehrgänge')
            for ktn in teilnehmer.kursteilnehmer:
                cal_res = CalculateResults(ktn)
                summary = cal_res.summary(session=session)
                lhg.append(
                    E('Lehrgang', titel=ktn.fernlehrgang.titel, ergebnis=summary['comment'])
                    )
            xml.append( 
                    E('TEILNEHMER',
                        E('Name', teilnehmer.name),
                        E('Vorname', teilnehmer.vorname),
                        E('Titel', nN(teilnehmer.titel)),
                        E('Anrede', nN(teilnehmer.anrede)),
                        E('Telefon', nN(teilnehmer.telefon)),
                        E('Email', nN(teilnehmer.email)),
                        E('Branche'),
                        E('Unternehmensklasse', nN(teilnehmer.kategorie)),
                        E('Erklaerung', teilnehmer.kompetenzzentrum),
                        E('Unternehmen',
                            E('Mitgliedsnummer', teilnehmer.unternehmen.mnr),
                            E('Name1', teilnehmer.unternehmen.name),
                            E('Name2', nN(teilnehmer.unternehmen.name2)),
                            E('Name3', nN(teilnehmer.unternehmen.name3)),
                            E('Strasse', nN(teilnehmer.unternehmen.str)),
                            E('PLZ', teilnehmer.unternehmen.plz),
                            E('ORT', teilnehmer.unternehmen.ort),
                            E('Ergaenzung'),
                        ),
                        lhg,
                    )
                    )
        else:
            xml.append(E('Mitgliedsummer', teilnehmer.unternehmen.mnr))
    open(fn, 'w').write(ET.tostring(xml, encoding="ISO-8859-15", xml_declaration=True, pretty_print=True))
    #print "Writing File %s" % fn
    #fn = makeZipFile(fn)
    return fn


@menuentry(ExportItems)
class ListeKompetenzzentrum(grok.View):
    grok.context(IFernlehrgang)
    grok.name('kompetenzzentrum')
    grok.title('Liste Kompetenzzentrum')

    def update(self):
        from fernlehrgang.tasks import export_liste_kompetenzzentrum 
        mail = getUserEmail(self.request.principal.id)
        fn = export_liste_kompetenzzentrum.delay(flg_id=self.context.id, mail=mail)
        print fn

    def render(self):
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
