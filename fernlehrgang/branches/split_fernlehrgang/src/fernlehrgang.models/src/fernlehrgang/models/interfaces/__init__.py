# -*- coding: utf-8 -*-

VOCABULARIES = {}

from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder


def named_vocabulary(name):
    @provider(IContextSourceBinder)
    def get_vocabulary(*args, **kwargs):
        vocabulary = VOCABULARIES.get(name)
        if vocabulary is None:
            raise KeyError(name)
        return vocabulary(*args, **kwargs)
    return get_vocabulary


def register_vocabulary(vocabulary, name):
    if name in VOCABULARIES:
        raise KeyError(name)
    VOCABULARIES[name] = vocabulary


from .antwort import IAntwort
from .flg import IFernlehrgang
from .lehrheft import ILehrheft
from .unternehmen import IUnternehmen
from .kursteilnehmer import IKursteilnehmer, lieferstopps
from .teilnehmer import ITeilnehmer, generatePassword
from .frage import IFrage
from .resultate import ICalculateResults
