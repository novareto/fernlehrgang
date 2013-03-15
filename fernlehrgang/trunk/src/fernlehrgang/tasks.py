# -*- coding: utf-8 -*-                                                         
# Copyright (c) 2007-2011 NovaReto GmbH                                         
# cklinger@novareto.de                                                          
                                                                                
import celery                                                                   
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fernlehrgang import models


celery_app = celery.Celery()                                                    
celery_app.config_from_object('celeryconfig')                                   


some_engine = create_engine('oracle://cklinger:thaeyoo2@oracle/XE')
Session = sessionmaker(bind=some_engine)

                                                                                
@celery_app.task                                                                
def export(a, b):
    session = Session()
    return session.query(models.Fernlehrgang.id).all()
