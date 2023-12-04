# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import sys
import logging
import zope.app.debug




logger = logging.getLogger("fernlehrgang")
#logging.basicConfig()
#logger = logging.getLogger()

def log(message, summary="", severity=logging.INFO):
    logging.log(severity, "%s %s", summary, message)


# SQLAlchemy LOGGING --> INFO for echo=True
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


def fmtDate(d):
    return "%02d.%02d.%02d" % (d.day, d.month, d.year)


def visit_sequence(self, sequence):
    nn = sequence.name
    if sequence.metadata.schema:
        nn = "%s.%s" % (sequence.metadata.schema, nn)
    return "NEXT VALUE FOR %s" % nn


try:
    from ibm_db_sa.base import DB2Compiler

    DB2Compiler.visit_sequence = visit_sequence
except Exception:
    pass



class NoDatabaseDebugger(zope.app.debug.Debugger):

    def root(self):
        return self.db



def interactive_debug_prompt(zope_conf):
    from megrok.nozodb.utils import config
    db = config(zope_conf)
    debugger = NoDatabaseDebugger.fromDatabase(db)
    from grokcore.startup.startup import _classic_debug_prompt
    if len(sys.argv) > 1:
        globals_ = {
            'debugger': debugger,
            'app': debugger,
            'root': debugger.root()}
        del sys.argv[0]
        globals_['__name__'] = '__main__'
        globals_['__file__'] = sys.argv[0]
        exec(open(sys.argv[0]).read(), globals_)
        sys.exit()
    return _classic_debug_prompt(debugger)
