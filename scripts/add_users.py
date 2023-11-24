# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import csv
import click

from fernlehrgang import models
from z3c.saconfig import Session
from zope.component.hooks import setSite
from fernlehrgang.interfaces.teilnehmer import generatePassword


STATUS = ('A1', 'A2')
BAD_FLG_IDS = ()

LOG = []
FID = 202
MNR = "995000221"


def check_teilnehmer(teilnehmer):
    if len(teilnehmer) == 0:
        return True
    for tn in teilnehmer:
        for ktn in tn.kursteilnehmer:
            if ktn.fernlehrgang.id < 115:
                return True
    return False

def worker(app, root):
    OK = 0
    OK_S = []
    #flg = root['app']
    setSite(root)
    session = Session()
    fernlehrgang = session.query(models.Fernlehrgang).get('157')
    with open('/tmp/flg_2023_endg.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for i, mnr in enumerate(reader):
            unternehmen = session.query(models.Unternehmen).filter(models.Unternehmen.mnr ==  mnr['MtglNr']).all()
            if unternehmen and len(unternehmen) == 1:
                unt = unternehmen[0]
                teilnehmer = unt.teilnehmer
                if check_teilnehmer(teilnehmer):
                    OK += 1
                    OK_S.append(('OK', mnr['MtglNr']))
                    print('IMPORT OK', mnr['MtglNr'])
                    teilnehmer = models.Teilnehmer()
                    teilnehmer.passwort = "passwort" #generatePassword()
                    teilnehmer.unternehmen_mnr = mnr['MtglNr']
                    unt.teilnehmer.append(teilnehmer)
                    session.flush()
                    print(teilnehmer.id)
                    kursteilnehmer = models.Kursteilnehmer(teilnehmer_id = teilnehmer.id, status="A2")
                    fernlehrgang.kursteilnehmer.append(kursteilnehmer)
                else:
                    OK_S.append(('!OK', "Teilnnehmer bereits vorhanden %s" % mnr['MtglNr']))
                    print('teilnehmer bereits vorhanden', mnr['MtglNr'])
            else:
                OK_S.append(('!OK', "Kein Unternehmen gefunden! %s" % mnr['MtglNr']))
                print('Not Found', mnr['MtglNr'])
                #teilnehmer = models.Teilnehmer()
                #teilnehmer.passwort = "passwort" #generatePassword()
                #teilnehmer.unternehmen_mnr = MNR
                #unternehmen.teilnehmer.append(teilnehmer)
                #session.flush()
                #print(teilnehmer.id)
                #kursteilnehmer = models.Kursteilnehmer(teilnehmer_id = teilnehmer.id, status="A2")
                #fernlehrgang.kursteilnehmer.append(kursteilnehmer)
    import transaction; transaction.commit()
    with open('/tmp/output.csv', 'w') as f:
        for x in OK_S:
            f.write(','.join(x) + '\n')
    print(OK)
if __name__ == "__main__":
    worker(app, root)
    exit()
