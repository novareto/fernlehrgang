# -*- coding: utf-8 -*-

import uvclight

from dolmen.content import IContent, schema
from uvclight.backends import patterns
from cromlech.sqlalchemy import get_session

from sqlalchemy import *
from sqlalchemy import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, relationship
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.context import push_store_context

from .interfaces import IQuizz
from fernlehrgang import models

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


class Member(patterns.Model):
   uvclight.context(IQuizz)

   pattern = 'member/:member_id'
   model = models.Teilnehmer

   @located
   def factory(member_id):
       session = get_session('fernlehrgang')()
       dd = session.query(models.Teilnehmer).filter(
            models.Teilnehmer.id == int(member_id)).one()
       return dd

   def arguments(teilnehmer):
       return dict(member_id = teilnehmer.id)


class Course(patterns.Model):
   uvclight.context(IQuizz)

   pattern = 'course/:fernlehrgang_id'
   model = models.Fernlehrgang

   @located
   def factory(fernlehrgang_id):
       session = get_session('fernlehrgang')
       dd = session.query(models.Fernlehrgang).filter(
            models.Fernlehrgang.id == int(fernlehrgang_id)).one()
       dd.storageid = 'fernlehrgang.%s' % fernlehrgang_id
       return dd

   def arguments(fernlehrgang):
       return dict(fernlehrgang_id = fernlehrgang.id)


class Lesson(patterns.Model):
    uvclight.context(IQuizz)

    pattern = "course/:fernlehrgang_id/lehrheft/:lehrheft_id"
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


def register_all(registry):
    models = frozenset((Member, Course, Lesson))
    patterns.register_models(registry, *models)
