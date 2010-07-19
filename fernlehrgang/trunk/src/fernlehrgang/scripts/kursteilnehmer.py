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
    session = Session()
    fernlehrgang = session.query(Fernlehrgang).get(options.fernlehrgang)
    for i, line in enumerate(DictReader(open(options.file, 'r'))):
        print i+1
        unternehmen = Session.query(Unternehmen).get(line['MNR'].replace('-', ''))
        if unternehmen:
            teilnehmer = Teilnehmer()
            unternehmen.teilnehmer.append(teilnehmer)
            session.flush()
            kursteilnehmer = Kursteilnehmer(teilnehmer_id = teilnehmer.id, 
                status = NICHT_REGISTRIERT)
            import pdb; pdb.set_trace() 
            fernlehrgang.kursteilnehmer.append(kursteilnehmer)
        if i == 100:
            break
    import transaction; transaction.commit()    
