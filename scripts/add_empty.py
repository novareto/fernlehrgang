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

def worker(app, root):
    #flg = root['app']
    setSite(root)
    session = Session()
    fernlehrgang = session.query(models.Fernlehrgang).get('127')
    unternehmen = session.query(models.Unternehmen).filter(models.Unternehmen.mnr == MNR).one()
    if unternehmen:
                teilnehmer = models.Teilnehmer()
                teilnehmer.passwort = "passwort" #generatePassword()
                teilnehmer.unternehmen_mnr = MNR
                unternehmen.teilnehmer.append(teilnehmer)
                session.flush()
                print(teilnehmer.id)
                kursteilnehmer = models.Kursteilnehmer(teilnehmer_id = teilnehmer.id, status="A2")
                fernlehrgang.kursteilnehmer.append(kursteilnehmer)
    import transaction; transaction.commit()

if __name__ == "__main__":
    worker(app, root)
    exit()
