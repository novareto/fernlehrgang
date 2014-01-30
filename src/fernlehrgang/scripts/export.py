# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from fernlehrgang.exports.statusliste import export
from fernlehrgang.exports.oflg import report


def main(dsn, flg_id):
    dsn = sys.argv[1]
    engine = create_engine(dsn)
    Session = sessionmaker(bind=engine)
    session = Session()
    return str(report(session))


def main_export(**kwargs):
    import plac; plac.call(main)
