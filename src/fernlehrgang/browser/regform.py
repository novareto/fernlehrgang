# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de 


import grok

from z3c.saconfig import Session
from fernlehrgang.models import Fernlehrgang, Unternehmen, Teilnehmer, Kursteilnehmer
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer, generatePassword
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.app import IFernlehrgangApp
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang import Form
from datetime import date, timedelta

from zeam.form.base import Fields
from zeam.form.base import action


class AutoRegForm(Form):
    grok.context(IFernlehrgangApp)
    grok.require('zope.Public')

    fields = Fields(IUnternehmen).select('mnr')
    fields += Fields(ITeilnehmer).omit('id')
    fields += Fields(IKursteilnehmer).omit('id', 'teilnehmer_id', 'gespraech')

    ignoreRequest = False

    def updateForm(self):
        super(AutoRegForm, self).updateForm()
        self.fields['passwort'].defaultValue = generatePassword()
        self.fields['erstell_datum'].defaultValue = date.today() 

    @action('Teilnehmer anlegen')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            return errors
        session = Session()
        unternehmen = session.query(Unternehmen).get(data.get('mnr'))
        if not unternehmen:
            self.flash(u'Das Unternehmen mit der Mitgliedsnummer %s existiert nicht' % data.get('mnr'))
            return 
        tn = Teilnehmer(
            name = data['name'],
            vorname = data['vorname'],
            passwort = data['passwort'],
            geburtsdatum = data['geburtsdatum'],
            ort = data['ort'],
            adresszusatz = data['adresszusatz'],
            plz = data['plz'],
            nr = data['nr'],
            strasse = data['strasse'],
            email = data['email'],
            anrede = data['anrede'],
            titel = data['titel'],
            telefon = data['telefon'],
            unternehmen_mnr=unternehmen.mnr,
        )
        unternehmen.teilnehmer.append(tn)
        session.flush()
        flg = session.query(Fernlehrgang).get(data['fernlehrgang_id'])
        kursteilnehmer = Kursteilnehmer(
            fernlehrgang_id=data.get('fernlehrgang_id'),
            status=data.get('status'),
            erstell_datum=data.get('erstell_datum'),
            un_klasse = data.get('un_klasse'),
            branche = data.get('branche'),
            unternehmen_mnr=data['mnr'])
        kursteilnehmer.teilnehmer = tn
        flg.kursteilnehmer.append(kursteilnehmer)
        session.flush()
        from zope.event import notify
        from zope.lifecycleevent import ObjectAddedEvent
        notify(ObjectAddedEvent(tn))
        self.flash('Der Teilnehmer wurde als Kursteilnehmer mit der ID %s angelegt.' % tn.id )
