# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import csv
from z3c.saconfig import Session
from fernlehrgang import models
import collections

#@timecall
def worker():
    y=[]
    session = Session()
    query = session.query(models.Kursteilnehmer.teilnehmer_id).filter(models.Kursteilnehmer.fernlehrgang_id==115)
    alle = query.all()
    print len(alle)
    for x in alle:
        y.append(x[0])
    counter=collections.Counter(y)
    i=0
    for x, y in counter.items():
        if y > 1:
            i+=1
            ktns = session.query(models.Kursteilnehmer).filter(
                models.Kursteilnehmer.teilnehmer_id == x, models.Kursteilnehmer.fernlehrgang_id==115).order_by(models.Kursteilnehmer.id).all()
            alt, neu = ktns
            print alt.id, neu.id
            if alt.id > neu.id:
                print "FUCK WHATS UP"
            session.delete(neu)
    import transaction; transaction.commit()
    



if __name__ == "__main__":
    worker()
    exit()
