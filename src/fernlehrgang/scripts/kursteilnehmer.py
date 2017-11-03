# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import sys
import os
import code
import zdaemon.zdctl
import zope.app.wsgi
import zope.app.debug

from csv import DictReader
from optparse import OptionParser
from zope.component import provideAdapter
from zope.dottedname.resolve import resolve
from zope.security.interfaces import IUnauthorized
from zope.publisher.interfaces import IReRaiseException
from zope.app.publication.zopepublication import ZopePublication

from z3c.saconfig import Session
from fernlehrgang.models import Fernlehrgang, Kursteilnehmer, Teilnehmer, Unternehmen
from fernlehrgang.interfaces.teilnehmer import generatePassword
from fernlehrgang import log
from sqlalchemy import and_


def parse_options():
    """ Wertet die Argumente aus und gibt diese zurueck
    """

    usage = """
    %prog [options]
    addkursteilnehmer 
    novareto GmbH 2009 info@novareto.de
    """
    parser = OptionParser(usage = usage)

    parser.add_option("-f", "--file",
        dest = "file",
        action = "store",
        help = u"""Bitte geben Sie einen vollständingen Pfad für das ImportFile an.
        """
    )

    parser.add_option("-i", "--id_fernlehrgang",
        dest = "fernlehrgang",
        action = "store",
        help = u"""Geben Sie an für welchen Fernlehrgang dieses File importiert werden soll.
                  Achtung wir brauchen die ID des Fernlehrgangs.
        """
    )

    parser.add_option("-p", "--portal",
        dest = "portal",
        action = "store",
        help = u"""Geben Sie an für welches Portal dieses File importiert werden soll.
                  Achtung wir brauchen die ID des Portals http://localhost:8080/app.
                  app ist hier der richtige Parameter
        """
    )

    (options, args) = parser.parse_args()
    return (options, args, parser)



def main(argv=None):
    """ Script zum Anlegen von Kursteilnehmern"""

    NICHT_REGISTRIERT = "A2"

    # Einlesen der options
    if argv is None:
        argv = sys.argv
    options, args, parser = parse_options()
    if not options.file:
        parser.error("Bitte eine CSV-Datei angeben.")
    if not options.fernlehrgang:
        parser.error("Bitte geben Sie die ID des Fernlehrgangs an.")
    
    if not options.portal:
        parse.error("Bitte die Id des Portals angeben")

    # Setup der Site
    zope_conf=os.path.join('parts', 'etc', 'zope.conf')
    db = zope.app.wsgi.config(zope_conf)
    connection = db.open()
    root = connection.root()[ZopePublication.root_name]
    app = root[options.portal]
    
    # Logik
    mto = 0 
    tids = []
    err = []
    session = Session()
    fernlehrgang = session.query(Fernlehrgang).get(options.fernlehrgang)
    z = 0
    import pdb; pdb.set_trace() 
    for i, line in enumerate(DictReader(open(options.file, 'r'), delimiter=",")):
        if z < 18186:
            MNR = line['MNR'].strip().replace('-', '')
            if len(MNR) == 8:
                print "GROLA MNR"
                unternehmen = Session.query(Unternehmen).filter(and_(Unternehmen.mnr_g_alt == MNR, Unternehmen.mnr == Unternehmen.mnr_e)).all()
                if unternehmen:
                    if len(unternehmen) == 1:
                        unternehmen = unternehmen[0]
                    else:
                        import pdb; pdb.set_trace() 

                print "ACHTUNG GROLA"
            else:    
                unternehmen = Session.query(Unternehmen).get(MNR)
            i+=1
            #print '%s, %s %s' %(i, line['MNR'], unternehmen)
            if z in range(0, 20000, 1000):
                print z 
            if unternehmen:
                if len(unternehmen.teilnehmer) == 0:
                    teilnehmer = Teilnehmer()
                    teilnehmer.passwort = generatePassword()
                    if 'Name' in line.keys():
                        teilnehmer.name = line['Name'].strip().decode('iso-8859-15')
                    if 'Vorname' in line.keys():
                        teilnehmer.vorname = line['Vorname'].strip().decode('iso-8859-15')
                    #if 'Anrede' in line.keys():
                    #    teilnehmer.anrede = line['Anrede'].strip()
                    unternehmen.teilnehmer.append(teilnehmer)
                    session.flush()
                    kursteilnehmer = Kursteilnehmer(teilnehmer_id = teilnehmer.id, 
                        status = NICHT_REGISTRIERT)
                    tids.append(teilnehmer.id)
                    fernlehrgang.kursteilnehmer.append(kursteilnehmer)
                    print z
                    z += 1
                else:
                    print "Schon mehr als 1 Teilnehmer --> %s" % line['MNR']
                    mto += 1
            else:
                print "Kein Unternehmen gefunden --> %s" % line['MNR']
                err.append(line['MNR'])
    import transaction; transaction.commit()    
    print len(err)
    print "#" * 50
    ef = open('/tmp/bad_report.txt', 'w+')
    ef.write('\n'.join([str(x) for x in err]))
    ef.close()
    #for x in err:
    #    print x+','
    print "#" * 50
    #print tids
    print "STATISTIK"
    print "GESAMT", i
    print "OK", len(tids)
    fo = open('/tmp/good_report.txt', 'w+')
    fo.write('\n'.join([str(x) for x in tids]))
    fo.close()
    print "MEHR ALS 0", mto
    #foo = open('/tmp/more_then_one.txt', 'w+')
    #foo.write('\n'.join([str(x) for x in mto]))
    #foo.close()
    print "Kein Unternehmen", len(err)
