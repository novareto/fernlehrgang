# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import TypeDecorator, String

Base = declarative_base()


class MyStringType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None and dialect.name == "oracle":
            value = value.encode('utf-8')
        return value


from .fernlehrgang import IFernlehrgang, Fernlehrgang
from .unternehmen import IUnternehmen, Unternehmen
from .teilnehmer import ITeilnehmer, Teilnehmer, generatePassword
from .lehrheft import ILehrheft, Lehrheft
from .frage import IFrage, Frage, FrageBild
from .kursteilnehmer import IKursteilnehmer, Kursteilnehmer, lieferstopps
from .antwort import IAntwort, Antwort
from .resultate import ICalculateResults
