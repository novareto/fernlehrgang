# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import logging


logger = logging.getLogger('fernlehrgang')


def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)

# SQLAlchemy LOGGING --> INFO for echo=True
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


def fmtDate(d):
    return "%02d.%02d.%02d" % (d.day, d.month, d.year)


def visit_sequence(self, sequence):
    nn = sequence.name
    if sequence.metadata.schema:
        nn = "%s.%s" %(sequence.metadata.schema, nn)
    return "NEXT VALUE FOR %s" % nn

try:
    from ibm_db_sa.base import DB2Compiler
    DB2Compiler.visit_sequence = visit_sequence 
except Exception:
    pass
