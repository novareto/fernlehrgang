# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de

import grok
import datetime

from fernlehrgang.interfaces.flg import IFernlehrgang
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer, lieferstopps
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.models import Teilnehmer, Kursteilnehmer, JournalEntry
from fernlehrgang.viewlets import NavEntry
from megrok.traject import locate
from megrok.traject.components import DefaultModel
from sqlalchemy import and_
from fernlehrgang.slots.interfaces import IExtraInfo
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import NO_VALUE
from zeam.form.base import action
from zope.i18nmessageid import MessageFactory
from fernlehrgang.browser import Form, Display, EditForm

from zope.app.appsetup.product import getProductConfiguration
config = getProductConfiguration('gbo')
try:
    GBO_TOKEN = config.get('gbo_token')
except:
    raise "NO GBO TOKEN"


_ = MessageFactory("zeam.form.base")

grok.templatedir("templates")



class KursteilnehmerListing(Form):
    grok.context(IFernlehrgang)
    grok.name("kursteilnehmer_listing")
    grok.title("Kursteilnehmer verwalten")
    grok.order(10)

    fields = Fields(ITeilnehmer).select("id", "name", "geburtsdatum")

    label = u"Kursteilnehmer"
    description = u"Hier können Sie die Kursteilnehmer für Ihren Fernlehrgang suchen und bearbeiten."

    results = []

    def getResults(self):
        root = grok.getSite()
        lf_vocab = lieferstopps(None)
        for teilnehmer, kursteilnehmer in self.results:
            locate(root, kursteilnehmer, DefaultModel)
            # locate(root, teilnehmer.unternehmen, DefaultModel)
            name = '<a href="%s"> %s %s </a>' % (
                self.url(kursteilnehmer),
                teilnehmer.name,
                teilnehmer.vorname,
            )
            rcu = []
            for unt in teilnehmer.unternehmen:
                locate(root, unt, DefaultModel)
                rcu.append(
                    '<a href="%s"> %s %s </a>' % (self.url(unt), unt.mnr, unt.name)
                )
            r = dict(
                name=name,
                id=teilnehmer.id,
                status=lf_vocab.getTerm(kursteilnehmer.status).title,
                unternehmen=",".join(rcu),
            )
            yield r

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    @action(u"Suchen")
    def handle_search(self):
        v = False
        data, errors = self.extractData()
        session = Session()
        flg_id = self.context.id
        sql = session.query(Teilnehmer, Kursteilnehmer)
        sql = sql.filter(
            and_(
                Kursteilnehmer.fernlehrgang_id == flg_id,
                Kursteilnehmer.teilnehmer_id == Teilnehmer.id,
            )
        )
        if data.get("id") != "":
            sql = sql.filter(Teilnehmer.id == data.get("id"))
            v = True
        if data.get("name") != "":
            qu = "%%%s%%" % data.get("name")
            sql = sql.filter(Teilnehmer.name.ilike(qu))
            v = True
        if data.get("geburtsdatum") != NO_VALUE:
            sql = sql.filter(Teilnehmer.geburtsdatum == data.get("geburtsdatum"))
            v = True
        if not v:
            self.flash(u"Bitte geben Sie Suchkriterien ein.")
            return
        self.results = sql.all()


# @menuentry(AddMenu)
class AddKursteilnehmer(Form):
    grok.context(IFernlehrgang)
    grok.title(u"Kursteilnehmer")
    label = u"Kursteilnehmer anlegen"
    description = u"Kursteilnehmer anlegen"

    fields = Fields(IKursteilnehmer).select("teilnehmer_id")

    @action(u"Suchen und Registrieren")
    def handleSearch(self):
        data, errors = self.extractData()
        if errors:
            return
        session = Session()
        sql = session.query(Teilnehmer).filter(
            Teilnehmer.id == data.get("teilnehmer_id")
        )
        if sql.count() == 0:
            self.flash(
                "Es wurde kein Teilnehmer mit der ID %s gefunden"
                % data.get("teilnehmer_id")
            )
        teilnehmer = sql.one()
        locate(grok.getSite(), teilnehmer, DefaultModel)
        self.redirect(self.url(teilnehmer, "register"))


class KTNavEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.name('ktnav_entry')
    grok.order(10)

    title = "Kursteilnehmer"
    icon = "fas fa-user-tie"

    def url(self):
        return self.view.url(self.context)


class Index(Display):
    grok.context(IKursteilnehmer)
    grok.title(u"View")
    title = label = u"Kursteilnehmer"
    description = u"Details zum Kursteilnehmer"

    fields = Fields(IKursteilnehmer).omit(id)


class Edit(EditForm):
    grok.context(IKursteilnehmer)
    grok.name("edit")
    grok.title(u"Edit")

    fields = Fields(IKursteilnehmer).omit("id")
    fields["teilnehmer_id"].mode = "hiddendisplay"
    fields["fernlehrgang_id"].mode = "hiddendisplay"


class KTFristNavEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.name('kt_fristnav_entry')
    grok.order(20)

    title = "Fristverlängerung"
    icon = "fas fa-calendar-alt"

    def url(self):
        return self.view.url(self.context, 'extend_date')


class ExtendDate(Form):
    grok.context(IKursteilnehmer)
    grok.title(u"Fristverlängerung")
    grok.name("extend_date")

    title = u"Fristverlängerung"
    description = u"Hier können Sie die Frist für den OFLG neu setzen"

    fields = Fields(IKursteilnehmer).select("erstell_datum")
    fields["erstell_datum"].title = u"Fristverlängerung"
    fields["erstell_datum"].description = u"Fristverlängerung"

    def updateWidgets(self):
        super(ExtendDate, self).updateWidgets()
        dd = self.fieldWidgets.get("form.field.erstell_datum")
        import datetime

        now = datetime.datetime.now() + datetime.timedelta(days=30)
        dd.value = {"form.field.erstell_datum": now.strftime("%d.%m.%Y")}

    @action(u"Frist verlängern")
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            return
        self.context.status = u"A1"
        self.context.erstell_datum = data["erstell_datum"] - datetime.timedelta(
            days=365
        )
        self.context.teilnehmer.journal_entries.append(
            JournalEntry(
                status="info",
                type=u"FL %s %s - %s"
                % (
                    self.context.fernlehrgang.titel,
                    self.context.fernlehrgang.jahr,
                    data["erstell_datum"].strftime("%d.%m.%Y"),
                ),
                kursteilnehmer_id=self.context.id,
                teilnehmer_id=self.context.teilnehmer.id,
            )
        )
        self.flash(
            u"Die Frist für die Fertigstellung des Online-Fernlehrgangs wurde bis zum %s verlängert"
            % data["erstell_datum"].strftime("%d.%m.%Y")
        )


class MoreInfoOnKursteilnehmer(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IKursteilnehmer)

    def update(self):
        url = grok.url(self.request, self.context)
        self.script = "<script> var base_url = '%s'; </script>" % url
        locate(grok.getSite(), self.context.teilnehmer, DefaultModel)
        self.turl = '<a href="%s/edit"> %s %s </a>' % (
            self.view.url(self.context.teilnehmer),
            self.context.teilnehmer.name,
            self.context.teilnehmer.vorname,
        )


class KTReseendNavEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.name('kt_resend_entry')
    grok.order(30)

    title = "Übertrag GBO"
    icon = "fas fa-calendar-alt"

    def url(self):
        return self.view.url(self.context, 'transfer_gbo')


class ReSendGBO(Form):
    grok.context(IKursteilnehmer)
    grok.title(u'Übertragung - GBO')
    grok.name('transfer_gbo')

    title = u"Ergebnisübermittlung - GBO"
    description = u"Hier können Sie erneut Ergebnisse an die GBO übertragen."

    def update(self):
        if not self.context.fernlehrgang.typ == '4':
            self.flash(u'Die Übertragung der Datzen zu GBO funktioniert nur für Lehrgänge vom Type "Virtuelle Lernwelt"')
            self.redirect(self.url(self.context))

        elif len(self.context.antworten) == 0:
            self.flash(u'Dieser Teilnehemr hat noch keine Antworten von der Virtuellen Lernwelt übermittelt')
            self.redirect(self.url(self.context))


    def generateGBOData(self, gbo_daten):
        ktn = self.context
        teilnehmer = ktn.teilnehmer
        unternehmen = teilnehmer.unternehmen[0]
        ftitel = teilnehmer.titel
        if ftitel == '0':
            ftitel = ''

        status = '0'
        if unternehmen.mnr in ('995000221', '995000230'):
            status = '1'
            print('STATUS TEST')

        res = dict()
        res['token'] = GBO_TOKEN

        res['client'] = dict(
            #number = teilnehmer.unternehmen_mnr,
            #mainnumber = teilnehmer.unternehmen_mnr,
            status = status,
            unternehmensnummer = unternehmen.unternehmensnummer or '2',
            unternehmens_az=unternehmen.mnr,
            betriebsstaetten_az=unternehmen.hbst or '2',
            name = unternehmen.name,
            zip = unternehmen.plz,
            city = unternehmen.ort,
            street = unternehmen.str,
            compcenter = 0,
        )
        res['user'] = dict(
            login = str(teilnehmer.id),
            salutation=int(teilnehmer.anrede),
            title=ftitel,
            firstname=teilnehmer.vorname,
            lastname=teilnehmer.name,
            phone=teilnehmer.telefon or '',
            email=teilnehmer.email or ''
        )
        res['orgas'] = gbo_daten['orgas']
        return res


    @action(u'Ergebnisse übertragen')
    def handle_transfer(self):
        data, errors = self.extractData()
        if errors:
            return
        from simplejson import loads
        gbo_daten = loads(self.context.antworten[0].gbo_daten)
        if not 'token' in gbo_daten:
            print("We have to create the REAL REQUEST")
        gbo_daten = self.generateGBOData(gbo_daten)
        print(gbo_daten)

        from fernlehrgang.api.gbo import GBOAPI
        gbo_api = GBOAPI()
        print(gbo_api.url)
        r = gbo_api.set_data(gbo_daten)
        print(r)
        gbo_status = r.status_code
        je = JournalEntry(type="Daten manuell zur GBO gesendet", status=gbo_status, kursteilnehmer_id=self.context.id)
        self.context.teilnehmer.journal_entries.append(je)
        self.flash(u'Die Ergebnisse für den Teilnehmer %s wurden erneut an die GBO übertragen. %s' % (self.context.teilnehmer_id, gbo_status))

    @action(u'Abbrechen')
    def handle_cancel(self):
        self.flash(u'Die Aktion wurde abgebrochen')
        self.redirect(self.url(self.context))


class KTDeleteProcessEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.baseclass()
    grok.name('delete_progress_vlw')
    grok.order(30)

    title = "VLW zurücksetzen"
    icon = "fas fa-calendar-alt"

    def url(self):
        return self.view.url(self.context, 'delete_progress_vlw')


class DeleteProgressCreate(Form):
    grok.context(IKursteilnehmer)
    grok.title(u'Lehrgang zurück setzen')
    grok.name('delete_progress_vlw')

    title = u"Lehrgangsfortschrit Virtuelle Lernwelt zurück setzen"
    description = u"Hier können Sie den Lehrgangfortschritt in der Virtuellen Lernwelt zurück setzen."

    @action(u'Zurücksetzen')
    def handle_transfer(self):
        data, errors = self.extractData()
        if errors:
            return
        ktn = self.context
        teilnehmer = ktn.teilnehmer
        results = {
            'teilnehmer_id': teilnehmer.id,
            'kursteilnehmer_id': ktn.id,
            'fernlehrgang_id': '116'
        }
        from kombu import Connection
        import json
        with Connection('amqp://guest:guest@localhost:5672//') as conn:
            simple_queue = conn.SimpleQueue('vlwd.reset_progress')
            message = json.dumps(results)
            simple_queue.put(message)
            print('Sent: %s' % message)
            simple_queue.close()
        self.flash(u'Der Lehrgangs Fortschritt wurde in der Virtuellen Lernwelt zurückgesetzt')
        self.redirect(self.url(self.context))

    @action(u'Abbrechen')
    def handle_cancel(self):
        self.flash(u'Die Aktion wurde abgebrochen')
        self.redirect(self.url(self.context))




class MoreInfoOnKursteilnehmerResults(grok.Viewlet):
    grok.viewletmanager(IExtraInfo)
    grok.context(IKursteilnehmer)
    grok.view(ReSendGBO)


class KTPrintNavEntry(NavEntry):
    grok.context(IKursteilnehmer)
    grok.name('kt_print_entry')
    grok.order(30)

    title = "Zertifikat"
    icon = "fas fa-download"

    def url(self):
        return self.view.url(self.context, 'pdf')


class PrintCertificate(grok.View):
    grok.context(IKursteilnehmer)
    grok.title(u'Zertifikat')
    grok.name('pdf')

    def render(self):
        ktn = self.context
        teilnehmer = ktn.teilnehmer
        teilnehmer_id = ktn.teilnehmer.id
        #ktn = teilnehmer.getVLWKTN()
        from tempfile import NamedTemporaryFile
        from base64 import encodestring
        from fernlehrgang.api.certpdf import createpdf, createfortpdf
        ftf = NamedTemporaryFile()
        from datetime import datetime

        try:
            pdate = ktn.antworten[0].datum.strftime('%d.%m.%Y')
        except:
            pdate = datetime.now().strftime('%d.%m.%Y')

        unr = ""
        if teilnehmer.unternehmen[0].unternehmensnummer:
            unr = str(teilnehmer.unternehmen[0].unternehmensnummer)
        typ = ktn.fernlehrgang.typ
        if typ in ("3", "5"):
            fh = createfortpdf(ftf, {
                "druckdatum": pdate,
                "flg_titel": ktn.fernlehrgang.titel,
                "teilnehmer_id": teilnehmer_id,
                "anrede": teilnehmer.anrede,
                "flg_id": str(ktn.fernlehrgang.id),
                "mnr": unr,
                "vorname": teilnehmer.vorname,
                "name": teilnehmer.name,
            })
        else:
            fh = createpdf(ftf, {
                "druckdatum": pdate,
                "flg_titel": ktn.fernlehrgang.titel,
                "teilnehmer_id": teilnehmer_id,
                "anrede": teilnehmer.anrede,
                "flg_id": str(ktn.fernlehrgang.id),
                "mnr": unr,
                "vorname": teilnehmer.vorname,
                "name": teilnehmer.name,
            })
        fh.seek(0)
        content_type = "application/pdf"
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', content_type )
        RESPONSE.setHeader(
        'content-disposition', 'attachment; filename=%s' % "Zertifikat.pdf")
        return fh.read() 
