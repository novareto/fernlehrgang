# -*- coding: utf-8 -*-                                                         
# Copyright (c) 2007-2011 NovaReto GmbH                                         
# cklinger@novareto.de                                                          
                                                                                
from fernlehrgang import models
from fernlehrgang.lib.emailer import send_mail

import logging
import celeryconfig
import zope.app.wsgi

from celery.signals import worker_process_init
from nva.asynctask.task import zope_task, transactional_task
from celery import task
from z3c.saconfig import Session
from fernlehrgang import logger


@worker_process_init.connect
def setupZCA(signal, sender):
    zope.app.wsgi.config(celeryconfig.ZOPE_CONF)
    logger.log(logging.INFO, 'Starting Zope/Grok ENVIRONMENT')


text = """ Im Anhang finden Sie die entsprechende Datei"""

                                                                                
#@zope_task                                                                
#def export_abschlussliste_fernlehrgang(flg_id, lh_id, lh, rdatum, stichtag, dateiname, mail="cklinger@novareto.de"):
#    from fernlehrgang.exports.abschlussliste_fernlehrgang import export
#    session = Session()
#    fn = export(session, flg_id, lh_id, lh, rdatum, stichtag, dateiname) 
#    send_mail('flgapp@bghw.de', (mail,), "Versandliste Fernlehrgang", text, [fn,]) 


#@zope_task                                                                
#def export_versandliste_fernlehrgang(flg_id, lh_id, lh, rdatum, stichtag, dateiname, mail="cklinger@novareto.de"):
#    from fernlehrgang.exports.versandliste_fernlehrgang import export
#    session = Session()
#    fn = export(session, flg_id, lh_id, lh, rdatum, stichtag, dateiname) 
#    send_mail('flgapp@bghw.de', (mail,), "Versandliste Fernlehrgang", text, [fn,]) 


#@zope_task                                                                
#def export_versandliste_fortbildung(flg_ids, stichtag, mail="cklinger@novareto.de"):
#    from fernlehrgang.exports.versandliste_fortbildung import export
#    session = Session()
#    fn = export(session, flg_ids, stichtag) 
#    send_mail('flgapp@bghw.de', (mail,), "Versandliste Fortbildung", text, [fn,]) 


#@zope_task                                                                
#def export_statusliste(flg_id, mail="cklinger@novareto.de"):
#    from fernlehrgang.exports.statusliste import export
#    session = Session()
#    fn = export(session, flg_id) 
#    send_mail('flgapp@bghw.de', (mail,), "Statusliste", text, [fn,]) 


#@zope_task                                                                
#def export_liste_kompetenzzentrum(flg_id, mail="cklinger@novareto.de"):
#    from fernlehrgang.exports.listekompetenzzentrum import export
#    session = Session()
#    fn = export(session, flg_id) 
#    send_mail('flgapp@bghw.de', (mail,), "Liste Kompetenzzentrum", text, [fn,]) 


from nva.asynctask.conf import celery_app
import transaction

@celery_app.task
def notifications_for_ofg():
    #from fernlehrgang.exports.oflg import report
    with transaction.manager as tm:
        session = Session()
        #rreport(session)
        mail = "ck@novareto.de"
        send_mail('fernlehrgang@bghw.de', (mail,), "TEST", text) 
        from fernlehrgang import logger
        1/0
        logger.log(logging.DEBUG, 'STARTING DAILY WORK')
