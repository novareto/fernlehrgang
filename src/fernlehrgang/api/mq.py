# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import sys
import logging
import simplejson
import transaction
import zope.app.wsgi

from fernlehrgang import log
from fernlehrgang import logger
from datetime import datetime
from kombu.log import get_logger
from z3c.saconfig import Session
from zope.interface import implementer
from kombu.mixins import ConsumerMixin
from zope.component.hooks import setSite
from kombu import Connection, Exchange, Queue
from transaction.interfaces import IDataManager
from fernlehrgang.interfaces.resultate import ICalculateResults

from sqlalchemy.exc import IntegrityError

from zope.app.appsetup.product import getProductConfiguration
config = getProductConfiguration('gbo')
try:
    GBO_TOKEN = config.get('gbo_token')
except:
    GBO_TOKEN = "218FD67F-1B71-48D0-9254-FF97E4091264"


class Message(object):

    def __init__(self, type, routing_key=None, **data):
        self.data = data
        self.type = type
        self.routing_key = routing_key

    @property
    def id(self):
        return self.__hash__()

    def dump(self):
        return self.data

    @staticmethod
    def publish(payload, connection, queue, routing_key):
        exchange = queue.exchange
        with connection.Producer(serializer='json') as producer:
            producer.publish(
                payload,
                exchange=exchange,
                routing_key=routing_key,
                declare=[queue]
            )


@implementer(IDataManager)
class MQDataManager(object):

    def __init__(self, url, queues):
        self.url = url
        self.queues = queues
        self.messages = {}

    def createMessage(self, message):
        if message.__hash__() in self.messages.keys():
            raise ValueError('%s MessageHash already there' % message.__hash__())
        self.messages[message.id] = message

    def commit(self, transaction):
        with Connection(self.url) as conn:
            while self.messages:
                uid, message = self.messages.popitem()
                payload = message.dump()
                queue = self.queues.get(message.type)
                if queue:
                    message.publish(payload, conn, queue, message.routing_key)
                    print('Sending Message to queue %s' % queue)

    def abort(self, transaction):
        self.messages = {}

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def tpc_abort(self, transaction):
        pass

    def sortKey(self):
        return "~nva.mq"


class MQTransaction(object):

    def __init__(self, url, queues, transaction_manager=None):
        self.url = url
        self.queues = queues
        if transaction_manager is None:
            transaction_manager = transaction.manager
        self.transaction_manager = transaction_manager

    def __enter__(self):
        dm = MQDataManager(self.url, self.queues)
        self.transaction_manager.join(dm)
        return dm

    def __exit__(self, type, value, traceback):
        pass


vlw_exchange = Exchange('vlwd.antwort', 'direct', durable=True)
vlw_queue = Queue('vlwd.antwort', exchange=vlw_exchange)

status_exchange = Exchange('vlwd.status', 'direct', durable=True)
status_exchange_e = Exchange('vlwd.status.error', 'direct', durable=True)
status_queue = Queue('vlwd.status', exchange=status_exchange)
status_queue_error = Queue('vlwd.status.error', exchange=status_exchange_e)

log_exchange = Exchange('vlwd.log', 'direct', durable=True)
log_queue = Queue('vlwd.log', exchange=log_exchange)


ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


QUEUES = {'results': status_queue, 'results_error': status_queue_error}


class Worker(ConsumerMixin):

    _conn = None

    def __init__(self, connection, db, url):
        self.connection = connection
        self.zodb = db
        self.url = url

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(queues=[vlw_queue, ], accept=['pickle', 'json'], callbacks=[self.run_task]),
            Consumer(queues=[log_queue, ], accept=['pickle', 'json'], callbacks=[self.setLogEntry]),
        ]

    def run_task(self, body, message):
        logger.info('START ADDING RESULTS')
        connection = self.zodb.open()
        root = connection.root()
        try:
            with transaction.manager as tm:
                app = root['Application']['app']
                setSite(app)
                results = self.saveResult(body)
                logger.info(results)
                newmessage = Message('results', data=results)
                with MQTransaction(self.url, QUEUES, transaction_manager=tm) as mqtm:
                    mqtm.createMessage(newmessage)
                message.ack()
        except StandardError:
            logger.error('task raised exception: %r', e)
            #message.ack()
            logger.exception('ERRROR')
        except IntegrityError:
            #message.ack()
            logger.exception('IntegryError')
        except:
            logger.exception('Error')

    def createGBODaten(self, ktn, orgas):
        teilnehmer = ktn.teilnehmer
        unternehmen = teilnehmer.unternehmen[0]
        ftitel = teilnehmer.titel
        if ftitel == '0':
            ftitel = ''
        res = dict()
        res['token'] = GBO_TOKEN 
        res['client'] = dict(
            number = teilnehmer.unternehmen_mnr,
            mainnumber = teilnehmer.unternehmen_mnr,
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
        res['orgas'] = orgas
        return res

    def createStatusUpdate(self, data, gbo_status):
        return data

    def saveResult(self, body):
        from fernlehrgang import models
        session = Session()
        data = simplejson.loads(body)
        teilnehmer_id = data.pop('teilnehmer_id')
        ktn = session.query(models.Kursteilnehmer).get(int(data.get('kursteilnehmer_id')))
        data['datum'] = datetime.now()
        data['system'] = "Virtuelle Lernwelt"
        data['gbo'] = "OK"
        orgas = data.pop('orgas')
        gbo_daten = self.createGBODaten(ktn, orgas)
        data['gbo_daten'] = simplejson.dumps(gbo_daten)
        data['lehrheft_id'] = 1137 
        data['frage_id'] = 10720
        gbo_u = data.pop('gbo_uebermittlung')
        data.pop('status')
        antwort = models.Antwort(**data)
        ktn.antworten.append(antwort)

        je = models.JournalEntry(type="Abschluss Virtuelle Lernwelt", status="1", kursteilnehmer_id=ktn.id)
        #ktn.teilnehmer.journal_entries.append(je)
        gbo_status=""
        if gbo_u:
            from fernlehrgang.api.gbo import GBOAPI
            gbo_api = GBOAPI()
            r = gbo_api.set_data(gbo_daten)
            logger.info(r.text)
            gbo_status = r.status_code
            je = models.JournalEntry(type="Daten nach GBO gesendet", status=gbo_status, kursteilnehmer_id=ktn.id)
            ktn.teilnehmer.journal_entries.append(je)
        result = ICalculateResults(ktn).summary()
        result['kursteilnehmer_id'] = data.get('kursteilnehmer_id')
        result['teilnehmer_id'] = teilnehmer_id
        result['ist_gespeichert'] = True
        result['an_gbo_uebermittelt'] = gbo_u
        result['gbo_comment'] = gbo_status
        status = "1"
        if result['comment'] == u'Nicht Bestanden, da das Abschlussgespräch noch nicht geführt wurde.':
            status = "4"
        je = models.JournalEntry(type="Abschluss Virtuelle Lernwelt", status=status, kursteilnehmer_id=ktn.id)
        ktn.teilnehmer.journal_entries.append(je)
        return result

    def setLogEntry(self, body, message):
        def true_false(v):
            if v:
                return "ja"
            else:
                return "nein"
        logger.info('GET A NEW LOG ENTRY')
        log_entry = simplejson.loads(body)
        logger.info(log_entry)
        from fernlehrgang import models
        typ = log_entry.pop('typ')
        if typ == "ausstattung":
            log_entry['type'] = u"Büro %s, Lager %s, Verwaltung %s" % (
                true_false(log_entry.pop('buero')),
                true_false(log_entry.pop('lager')),
                true_false(log_entry.pop('verkauf')))
            log_entry['type'] = log_entry['type'][:400]
        elif typ == "fortschritt":
            if 'position' in log_entry.keys():
                log_entry.pop('position')
            if 'title' not in log_entry:
                log_entry['title'] = ''

            log_entry['type'] = u"Lernfortschritt: %s (%s) zu %s % abgeschlossen." % (
                log_entry.pop('title'),
                log_entry.pop('key'),
                int(log_entry.pop('progress')))
            log_entry['type'] = log_entry['type'][:400]
        elif typ == "druck":
             log_entry['type'] = u"Das Abschluss-Zertifkat wurde gedruckt."
        if 'kursteilnehmer_id' in log_entry and log_entry['kursteilnehmer_id']:
            log_entry['kursteilnehmer_id'] = int(log_entry['kursteilnehmer_id'])
        try:
            with transaction.manager as tm:
                session = Session()
                teilnehmer = session.query(models.Teilnehmer).get(int(log_entry.get('teilnehmer_id')))
                if teilnehmer:
                    log_entry['status'] = "2"
                    je = models.JournalEntry(**log_entry)
                    teilnehmer.journal_entries.append(je)
                    message.ack()
        except StandardError:
            logger.error('Error in Logging %r', e)
            logger.exception('Error')


def main(url, conf):
    db = zope.app.wsgi.config(conf)
    with Connection(url) as conn:
        try:
            worker = Worker(conn, db, url)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
