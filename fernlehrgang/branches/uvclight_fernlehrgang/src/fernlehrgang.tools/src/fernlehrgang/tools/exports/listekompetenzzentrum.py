# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 
import uvclight

from fernlehrgang import models
from fernlehrgang.app.browser.ergebnisse import CalculateResults
from fernlehrgang.tools.exports.menus import ExportItems
from fernlehrgang.models.fernlehrgang import IFernlehrgang
from fernlehrgang.app.lib import nN
from openpyxl.workbook import Workbook
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, joinedload
from fernlehrgang.models.kursteilnehmer import un_klasse, gespraech
from fernlehrgang.tools.exports.utils import page_query, makeZipFile, getUserEmail
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
            models.Teilnehmer.kompetenzzentrum == "ja",
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
    xml = E('Komptenzzentrum')
    print rc.count()
    i=1
    for teilnehmer in rc:
        print i
        i+=1
        lhg = E(u'Lehrgänge')
        for ktn in teilnehmer.kursteilnehmer:
            cal_res = CalculateResults(ktn)
            summary = cal_res.summary()
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
                        E('Name1', teilnehmer.unternehmen.name),
                        E('Name2', nN(teilnehmer.unternehmen.name2)),
                        E('Name3', nN(teilnehmer.unternehmen.name3)),
                        E('PLZ', teilnehmer.unternehmen.plz),
                        E('ORT', teilnehmer.unternehmen.ort),
                        E('Ergaenzung'),
                    ),
                    lhg,
                )
                )
    open(fn, 'w').write(ET.tostring(xml, encoding="ISO-8859-15", xml_declaration=True, pretty_print=True))
    #print "Writing File %s" % fn
    #fn = makeZipFile(fn)
    return fn


@uvclight.menuentry(ExportItems)
class ListeKompetenzzentrum(uvclight.View):
    uvclight.context(IFernlehrgang)
    uvclight.name('kompetenzzentrum')
    uvclight.title('Liste Kompetenzzentrum')

    def update(self):
        from fernlehrgang.app.tasks import export_liste_kompetenzzentrum 
        mail = getUserEmail(self.request.principal.id)
        fn = export_liste_kompetenzzentrum(flg_id=self.context.id, mail=mail)
        print fn

    def render(self):
        self.flash('Sie werden benachrichtigt wenn der Report erstellt ist')
        self.redirect(self.application_url())
