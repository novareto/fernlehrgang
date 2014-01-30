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
#DSN = "oracle://flgprod:prodflg!@10.30.4.95/BGETest"
print DSN
if DSN:
    some_engine = create_engine(DSN)
    Session = sessionmaker(bind=some_engine)
else:
    raise "NO ENVIRONMENT FOR DSN SET"

text = """ Im Anhang finden Sie die entsprechende Datei"""

                                                                                
@celery_app.task                                                                
def export_abschlussliste_fernlehrgang(flg_id, lh_id, lh, rdatum, stichtag, dateiname, mail="cklinger@novareto.de"):
    from fernlehrgang.exports.abschlussliste_fernlehrgang import export
    session = Session()
    fn = export(session, flg_id, lh_id, lh, rdatum, stichtag, dateiname) 
    send_mail('flgapp@bghw.de', (mail,), "Versandliste Fernlehrgang", text, [fn,]) 


@celery_app.task                                                                
def export_versandliste_fernlehrgang(flg_id, lh_id, lh, rdatum, stichtag, dateiname, mail="cklinger@novareto.de"):
    from fernlehrgang.exports.versandliste_fernlehrgang import export
    session = Session()
    fn = export(session, flg_id, lh_id, lh, rdatum, stichtag, dateiname) 
    send_mail('flgapp@bghw.de', (mail,), "Versandliste Fernlehrgang", text, [fn,]) 


@celery_app.task                                                                
def export_versandliste_fortbildung(flg_ids, stichtag, mail="cklinger@novareto.de"):
    from fernlehrgang.exports.versandliste_fortbildung import export
    session = Session()
    fn = export(session, flg_ids, stichtag) 
    send_mail('flgapp@bghw.de', (mail,), "Versandliste Fortbildung", text, [fn,]) 


@celery_app.task                                                                
def export_statusliste(flg_id, mail="cklinger@novareto.de"):
    from fernlehrgang.exports.statusliste import export
    session = Session()
    fn = export(session, flg_id) 
    send_mail('flgapp@bghw.de', (mail,), "Statusliste", text, [fn,]) 


@celery_app.task                                                                
def export_liste_kompetenzzentrum(flg_id, mail="cklinger@novareto.de"):
    from fernlehrgang.exports.listekompetenzzentrum import export
    session = Session()
    fn = export(session, flg_id) 
    send_mail('flgapp@bghw.de', (mail,), "Liste Kompetenzzentrum", text, [fn,]) 


@celery_app.task
def notifications_for_ofg():
    from fernlehrgang.exports.oflg import report
    session = Session()
    report(session)

