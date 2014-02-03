# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MyStringType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None and dialect.name == "oracle":
            value = value.encode('utf-8')
        return value


    
from .models import (
    Fernlehrgang, Unternehmen, Teilnehmer,
    Lehrheft, Frage, FrageBild, Kursteilnehmer, Antwort)
