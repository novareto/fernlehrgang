# -*- coding: utf-8 -*-                                                         
# Copyright (c) 2007-2011 NovaReto GmbH                                         
# cklinger@novareto.de                                                          
                                                                                
import celery                                                                   
from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fernlehrgang import models
from zope.app.appsetup.product import getProductConfiguration
from fernlehrgang.lib.emailer import send_mail


celery_app = celery.Celery()                                                    
celery_app.config_from_object('celeryconfig')                                   

DSN = environ.get('DSN')
if DSN:
    some_engine = create_engine(DSN)
    Session = sessionmaker(bind=some_engine)
else:
    raise "NO ENVIRONMENT FOR DSN SET"

text = """ Im Anhang finden Sie die entsprechende Datei"""

                                                                                
@celery_app.task                                                                
def export_versandliste_fernlehrgang(flg_id, lh_id, lh, rdatum, stichtag, dateiname):
    from fernlehrgang.exports.versandliste_fernlehrgang import export
    session = Session()
    fn = export(session, flg_id, lh_id, lh, rdatum, stichtag, dateiname) 
    send_mail('cklinger', ('ck@novareto.de',), "Versandliste Fernlehrgang", text, [fn,]) 


@celery_app.task                                                                
def export_versandliste_fortbildung(flg_ids, stichtag):
    from fernlehrgang.exports.versandliste_fortbildung import export
    session = Session()
    fn = export(session, flg_ids, stichtag) 
    send_mail('cklinger', ('ck@novareto.de',), "Versandliste Fortbildung", text, [fn,]) 


@celery_app.task                                                                
def export_statusliste(flg_id):
    from fernlehrgang.exports.statusliste import export
    session = Session()
    fn = export(session, flg_id) 
    send_mail('cklinger', ('ck@novareto.de',), "Statusliste", text, [fn,]) 
