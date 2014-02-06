# -*- coding: utf-8 -*-

import grok
from megrok import traject
from .app import Questionaries 
from fernlehrgang.models import Teilnehmer, Fernlehrgang, Lehrheft
from z3c.saconfig import Session
from sqlalchemy import and_
from fernlehrgang.models import IFernlehrgang


class MemberTraject(traject.Traject):
   grok.context(Questionaries)

   pattern = 'member/:member_id'
   model = Teilnehmer 

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

   def factory(fernlehrgang_id):
       session = Session()
       dd = session.query(Fernlehrgang).filter(
            Fernlehrgang.id == int(fernlehrgang_id)).one()
       return dd

   def arguments(fernlehrgang):
       return dict(fernlehrgang_id = fernlehrgang.id)


class LessonTraject(traject.Traject):
    grok.context(Questionaries)

    pattern = "course/:fernlehrgang_id/lehrheft/:lehrheft_id"
    model = Lehrheft

    def factory(fernlehrgang_id, lehrheft_id):
        session = Session()
        return  session.query(Lehrheft).filter(
            and_( Lehrheft.fernlehrgang_id == int(fernlehrgang_id),
                  Lehrheft.id == int(lehrheft_id))).one()

    def arguments(lehrheft):
        return dict(fernlehrgang_id = lehrheft.fernlehrgang_id,
                    lehrheft_id = lehrheft.id)
