# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger('fernlehrgang')


def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s %s', summary, message)


# SQLAlchemy LOGGING --> INFO for echo=True
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
