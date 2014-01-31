# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from .models import (
    Fernlehrgang, Unternehmen, Teilnehmer,
    Lehrheft, Frage, FrageBild, Kursteilnehmer, Antwort)
