# -*- coding: utf-8 -*-
import sys
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from fernlehrgang.exports.statusliste import export


def main(dsn, flg_id):
    dsn = sys.argv[1]
    engine = create_engine(dsn)
    Session = sessionmaker(bind=engine)
    session = Session()
    return str(export(session, 100))


def main_export(**kwargs):
    import plac; plac.call(main)
