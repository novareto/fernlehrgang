# -*- coding: utf-8 -*-

import grok
from .app import Questionaries 
from fernlehrgang.app.upload import IFileStore
from fernlehrgang.models import IFernlehrgang
from fernlehrgang.models import Teilnehmer, Fernlehrgang, Lehrheft
from megrok import traject
from sqlalchemy import and_
from z3c.saconfig import Session
from zope.location import ILocation, LocationProxy
from zope.interface import alsoProvides


def located(func):
    def proxify(*args, **kws):
        item = func(*args, **kws)
        if item is not None and not ILocation.providedBy(item):
            return LocationProxy(item)
        return item
    return proxify


class MemberTraject(traject.Traject):
   grok.context(Questionaries)

   pattern = 'member/:member_id'
   model = Teilnehmer

   @located
   def factory(member_id):
       session = Session()
       dd = session.query(Teilnehmer).filter(
            Teilnehmer.id == int(member_id)).one()
       return dd

   def arguments(teilnehmer):
       return dict(member_id = teilnehmer.id)


class CourseTraject(traject.Traject):
   grok.context(Questionaries)

   pattern = 'course/:fernlehrgang_id'
   model = Fernlehrgang

   @located
   def factory(fernlehrgang_id):
       session = Session()
       dd = session.query(Fernlehrgang).filter(
            Fernlehrgang.id == int(fernlehrgang_id)).one()
       dd.storageid = 'fernlehrgang.%s' % fernlehrgang_id
       alsoProvides(dd, IFileStore)
       return dd

   def arguments(fernlehrgang):
       return dict(fernlehrgang_id = fernlehrgang.id)


class LessonTraject(traject.Traject):
    grok.context(Questionaries)

    pattern = "course/:fernlehrgang_id/lehrheft/:lehrheft_id"
    model = Lehrheft

    @located
    def factory(fernlehrgang_id, lehrheft_id):
        session = Session()
        return  session.query(Lehrheft).filter(
            and_( Lehrheft.fernlehrgang_id == int(fernlehrgang_id),
                  Lehrheft.id == int(lehrheft_id))).one()

    def arguments(lehrheft):
        return dict(fernlehrgang_id = lehrheft.fernlehrgang_id,
                    lehrheft_id = lehrheft.id)
