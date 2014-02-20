# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

#['aapolloni', '12345', 'Alexandra Apolloni', 'uvc.reader', '\n']


from z3c.saconfig import Session
from fernlehrgang.models.user import User

session = Session()

for line in open('/tmp/users.csv', 'r').readlines():
    value = line.split(';')
    #import pdb; pdb.set_trace()
    session.add(
        User(login = unicode(value[0]), email=value[4].split(), real_name=value[2], password=value[1], role=value[3])
    )
import transaction; transaction.commit()
