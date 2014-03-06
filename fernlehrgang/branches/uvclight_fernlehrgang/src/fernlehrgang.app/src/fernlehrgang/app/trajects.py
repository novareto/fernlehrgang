# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 

import uvclight
from .upload import IFileStore

from dolmen.content import IContent, schema
from uvclight.backends import patterns
from cromlech.sqlalchemy import get_session

from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.context import push_store_context

from .upload import IFileStore
from .interfaces import IFernlehrgangApp
from fernlehrgang import models
from .auth.handler import Benutzer, Users

from dolmen.forms.base.markers import Marker
from zope.component import IFactory, provideUtility, getUtility
from zope.container.contained import Contained
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.interface import Interface, implementer, provider
from zope.interface import alsoProvides
from zope.location import LocationProxy, ILocation
from zope.publisher.interfaces import IStartRequestEvent

    
def located(func):
    def proxify(*args, **kws):
        item = func(*args, **kws)
        if item is not None and not ILocation.providedBy(item):
            return LocationProxy(item)
        return item
    return proxify


class BenutzerModel(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = Users
    pattern = "benutzer"

    @located
    def factory():
        return Benutzer

    def arguments():
        return dict()


class Fernlehrgang(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = models.Fernlehrgang
    pattern = "fernlehrgang/:fernlehrgang_id"

    @located
    def factory(fernlehrgang_id):
        session = get_session('fernlehrgang')
        dd = session.query(models.Fernlehrgang).filter(
            models.Fernlehrgang.id == int(fernlehrgang_id)).one()
        dd.storageid = 'fernlehrgang.%s' % fernlehrgang_id
        alsoProvides(dd, IFileStore)
        return dd

    def arguments(fernlehrgang):
        return dict(fernlehrgang_id = fernlehrgang.id)


class Unternehmen(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = models.Unternehmen
    pattern = "unternehmen/:unternehmen_mnr"

    @located
    def factory(unternehmen_mnr):
        session = get_session('fernlehrgang')
        return session.query(models.Unternehmen).filter(
            models.Unternehmen.mnr == unternehmen_mnr).one()

    def arguments(unternehmen):
        return dict(unternehmen_mnr = unternehmen.mnr)


class Teilnehmer(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = models.Teilnehmer
    pattern = "unternehmen/:unternehmen_mnr/teilnehmer/:id"

    @located
    def factory(id, unternehmen_mnr):
        session = get_session('fernlehrgang')
        return session.query(models.Teilnehmer).filter(
            and_(models.Teilnehmer.id == id,
                 models.Teilnehmer.unternehmen_mnr == unternehmen_mnr)).one()

    def arguments(teilnehmer):
        return dict(id=teilnehmer.id,
                    unternehmen_mnr=teilnehmer.unternehmen_mnr)


class Lehrheft(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    pattern = "fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id"
    model = models.Lehrheft

    @located
    def factory(fernlehrgang_id, lehrheft_id):
        session = get_session('fernlehrgang')
        return  session.query(models.Lehrheft).filter(
            and_(models.Lehrheft.fernlehrgang_id == int(fernlehrgang_id),
                 models.Lehrheft.id == int(lehrheft_id))).one()

    def arguments(lehrheft):
        return dict(fernlehrgang_id = lehrheft.fernlehrgang_id,
                    lehrheft_id = lehrheft.id)


class Frage(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = models.Frage
    pattern = "fernlehrgang/:fernlehrgang_id/lehrheft/:lehrheft_id/frage/:frage_id"

    @located
    def factory(fernlehrgang_id, lehrheft_id, frage_id):
        session = get_session('fernlehrgang')
        return  session.query(models.Frage).filter(
            and_(models.Frage.id == int(frage_id),
                 models.Frage.lehrheft_id == int(lehrheft_id))).one()

    def arguments(frage):
        return dict(frage_id = frage.id,
                    lehrheft_id = frage.lehrheft_id,
                    fernlehrgang_id = frage.lehrheft.fernlehrgang.id)


def frag_builder(**kwargs):
    if 'id' in kwargs:
        session = get_session('fernlehrgang')
        id = kwargs.pop('id')
        frage = session.query(models.Frage).filter(models.Frage.id == id).one()
    else:
        frage = models.Frage()
    return frage


provideUtility(frag_builder, IFactory,
               name='fernlehrgang.models.frage.IFrage')


class Kursteilnehmer(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = models.Kursteilnehmer
    pattern = ("fernlehrgang/:fernlehrgang_id/kursteilnehmer" +
               "/:kursteilnehmer_id")

    @located
    def factory(fernlehrgang_id, kursteilnehmer_id):
        session = get_session('fernlehrgang')
        return  session.query(models.Kursteilnehmer).filter(
            and_(models.Kursteilnehmer.fernlehrgang_id == int(fernlehrgang_id),
                 models.Kursteilnehmer.id == int(kursteilnehmer_id))).one()

    def arguments(kursteilnehmer):
        return dict(fernlehrgang_id = kursteilnehmer.fernlehrgang_id,
                    kursteilnehmer_id = kursteilnehmer.id)


class Antwort(patterns.Model):
    uvclight.context(IFernlehrgangApp)

    model = models.Antwort
    pattern = (
        "fernlehrgang/:fernlehrgang_id/kursteilnehmer/:kursteilnehmer_id" +
        "/antwort/:antwort_id")

    @located
    def factory(fernlehrgang_id, kursteilnehmer_id, antwort_id):
        session = get_session('fernlehrgang')
        return  session.query(models.Antwort).filter(
            and_(models.Antwort.id == int(antwort_id),
                 models.Antwort.kursteilnehmer_id == int(kursteilnehmer_id))
                 ).one()

    def arguments(antwort):
        return dict(antwort_id = antwort.id,
                    kursteilnehmer_id = antwort.kursteilnehmer_id,
                    fernlehrgang_id = antwort.kursteilnehmer.fernlehrgang.id)


def register_all(registry):
    models = frozenset((Fernlehrgang, Unternehmen, Teilnehmer, Lehrheft,
                        Frage,  Kursteilnehmer, Antwort, BenutzerModel))
    patterns.register_models(registry, *models)
