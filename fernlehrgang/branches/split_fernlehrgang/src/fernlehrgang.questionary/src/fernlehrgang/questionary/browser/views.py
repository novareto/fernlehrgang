# -*- coding: utf-8 -*-


import grok

from datetime import datetime
from dolmen.app.layout import models
from grokcore.chameleon.components import ChameleonPageTemplateFile
from sqlalchemy import and_
from z3c.saconfig import Session
from zeam.form.base import Fields
from zope.component import getMultiAdapter, getUtility
from zope.interface import Interface

from fernlehrgang.models import Kursteilnehmer, Antwort, Lehrheft
from fernlehrgang.models import IFernlehrgang, ILehrheft, IFrage
from fernlehrgang.models import ITeilnehmer, ICalculateResults

from .skin import IQuestionary
from ..app import Questionaries
from ..interfaces import IMembership


VALUES = frozenset(('A', 'B', 'C', 'D'))
MISSING = "Missing value"
BAD_VALUE = "Wrong value. Don't cheat"


grok.templatedir('templates')


class Index(models.Index):
    grok.context(Questionaries)
    grok.layer(IQuestionary)
    grok.require('zope.View')

    title = u"Whatever"

    def getCourses(self):
        membership = IMembership(self.request.principal, None)
        if membership is not None:
            return membership.courses
        return []


class CoursePage(models.Index):
    grok.context(IFernlehrgang)
    grok.name('index')
    grok.layer(IQuestionary)
    grok.require('zope.View')

    results = None
    title = u"Fernlehrgag"
    
    def update(self):
        membership = IMembership(self.request.principal, None)
        if membership is not None:
            self.results = membership.get_course_result(self.context.id)

    def getStatus(self, lession_id):
        ret = False
        membership = IMembership(self.request.principal, None)
        if membership is not None:
            ktn = membership.get_course_member(self.context.id)
            session = Session()
            q = session.query(Antwort, Lehrheft).filter(
                and_(
                    Antwort.kursteilnehmer_id == ktn.id,
                    Antwort.lehrheft_id == lession_id,
                    Lehrheft.id == lession_id,
                    Lehrheft.vdatum <= datetime.now(),
                )
            )
            res = int(q.count())
            if res > 0:
                ret = "erledigt"
            elif res == 0:
                ret = "offen"
        print ret
        return ret 


class QuestionRenderer(object):

    modes = {
        "display": ChameleonPageTemplateFile(
            'templates/questiondisplayview.cpt'),
        "edit": ChameleonPageTemplateFile(
            'templates/questioneditview.cpt'),
        "editchoice": ChameleonPageTemplateFile(
            'templates/questioneditchoiceview.cpt'),
            }

    def __init__(self, context, request, **data):
        self.context = context
        self.request = request
        self.data = data
        self.id = str(self.context.id)

    def namespace(self):
        return {}
        
    def default_namespace(self):
        if self.context.bilder.count():
            store = getUtility(Interface, name='ImageStore')
            image = self.context.bild.locate(store=store)
            thumb = self.context.thumbnail.locate(store=store)
        else:
            image = None
            thumb = None

        return {
            "view": self,
            "context": self.context,
            "request": self.request,
            "data": self.data,
            "image": image,
            "thumb": thumb,
            }

    def render(self, mode):
        template = self.modes.get(mode)
        if template is None:
            raise ValueError('No such mode %r' % mode)
        return template.render(self)

    @classmethod
    def batch(cls, lesson, request, name, **data):
        size = len(lesson.fragen)
        for idx, question in enumerate(lesson.fragen, 1):
            view = cls(question, request, **data)
            if name == "edit" and len(question.antwortschema) > 1:
                name = "editchoice"
            html = view.render(name)
            yield {
                'id': question.frage,
                'title': question.titel,
                'render': html,
                'idx': idx,
                'max': size,
                }


class LessonPage(models.Index):
    grok.context(ILehrheft)
    grok.name('index')
    grok.layer(IQuestionary)
    grok.require('zope.View')

    title = u"Lehrheft"

    @property
    def questions(self):
        return QuestionRenderer.batch(
            self.context, self.request, 'display')


class LessonAnswerPage(models.Index):
    grok.context(ILehrheft)
    grok.name('answer')
    grok.layer(IQuestionary)
    grok.require('zope.View')

    title = u"Lehrheft"
    submitted = False

    @property
    def questions(self):
        return QuestionRenderer.batch(
            self.context, self.request, 'edit', **self.data)

    def validate(self):
        errors = {}
        data = {}
        
        # first thing : check if the user CAN answer
        # meaning : does he have access and no answers yet.

        questions = list(self.context.fragen)
        for question in questions:
            qid = 'frage-%s' % question.id
            answer = self.request.form.get(qid)
            an = set(answer)
            if answer is None:
                errors[question.id] = MISSING
            elif not an.issubset(VALUES):
                errors[question.id] = BAD_VALUE
            else:
                data[question.id] = ''.join(an)
        return errors, data

    def persist(self, data):
        membership = IMembership(self.request.principal, None)
        if membership is not None:
            ktn = membership.get_course_member(self.context.fernlehrgang_id)
            for frage_id, antwortschema in data.items():
                import pdb; pdb.set_trace() 
                ktn.antworten.append(
                    Antwort(
                        lehrheft_id=self.context.id,
                        frage_id=frage_id,
                        antwortschema=antwortschema,
                        datum=datetime.now(),
                        system="Extranet",
                    )
                )
        print data
    
    def update(self):
        self.action = '%s/%s' % (self.url(self.context),
                                 grok.name.bind().get(self))
        if 'validate' in self.request.form:
            self.submitted = True
            errors, data = self.validate()
            if not errors:
                self.persist(data)
                self.flash('thank you')
                self.redirect(self.url(self.context))
            else:
                self.data = data
                self.errors = errors
                self.flash('Correct your errors')
        else:
            self.data = {}
            self.errors = {}
 

class MemberPage(models.DefaultView):
    grok.context(ITeilnehmer)
    grok.name('index')
    grok.layer(IQuestionary)
    grok.require('zope.View')

    title = u"Teilnehmer"

    fields = Fields(ITeilnehmer)


class MemberPageEdit(models.Edit):
    grok.context(ITeilnehmer)
    grok.layer(IQuestionary)
    grok.require('zope.View')

    title = u"Teilnehmer"

    fields = Fields(ITeilnehmer).omit('id')
