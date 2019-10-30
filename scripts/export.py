# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import csv
from z3c.saconfig import Session
from fernlehrgang import models
import collections
from profilehooks import profile, timecall
from memory_profiler import profile


#@timecall
@profile
#@mprofile
def worker():
    y=[]
    session = Session()
    query = session.query(models.Kursteilnehmer, models.Teilnehmer, models.Unternehmen).filter(
        models.Unternehmen.mnr == models.Teilnehmer.unternehmen_mnr,
        models.Kursteilnehmer.fernlehrgang_id == 115,
        models.Kursteilnehmer.teilnehmer_id == models.Teilnehmer.id).yield_per(1000).enable_eagerloads(False)
    alle = query.all()
    for x, y, z in alle:
        print x.id
    print len(alle) 



if __name__ == "__main__":
    worker()
    exit()
