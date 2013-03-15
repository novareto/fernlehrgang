# -*- coding: utf-8 -*-

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fernlehrgang import models
from fernlehrgang.browser.ergebnisse import CalculateResults


def export(session):
    """This should be the "shared" export function.
    """
    return CalculateResults(models.Kursteilnehmer)


def main_export(*args, **kws):
    dsn = sys.argv[1]
    engine = create_engine(dsn)
    Session = sessionmaker(bind=engine)
    session = Session()
    return str(export(session))
