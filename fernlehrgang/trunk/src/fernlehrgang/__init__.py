# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

### LOGGING
import logging
logger = logging.getLogger('fernlehrgang')

def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)

