# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import transaction
import zope.app.wsgi

from kombu import Connection
from kombu.log import get_logger
from zope.component import getUtility
from kombu.mixins import ConsumerMixin
from zope.component.hooks import setSite
from fernlehrgang.interfaces.resultate import ICalculateResults


from kombu import Connection, Exchange, Queue


from fernlehrgang import log
from kombu import Connection
from zope.component import getUtility
from zope.interface import implementer
from transaction.interfaces import IDataManager



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
            producer.publish( payload, exchange=exchange, routing_key=routing_key, declare=[queue])



@implementer(IDataManager)
class MQDataManager(object):

    def __init__(self, url, queues):
        self.url = url
        self.queues = queues
        self.messages = {}

    def createMessage(self, message):
        if message.__hash__() in self.messages.keys():
            raise ValueError('%s MessageHash already there' %message.__hash__())
        self.messages[message.id] = message

    def commit(self, transaction):
        with Connection(self.url) as conn:
            while self.messages:
                uid, message = self.messages.popitem()
                payload = message.dump()
                queue = self.queues.get(message.type)
                if queue:
                    message.publish(payload, conn, queue, message.routing_key)
                    log.debug('Sending Message to queue %s' %queue)

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
status_queue = Queue('vlwd.status', exchange=status_exchange)

QUEUES = {'results': status_queue}



logger = get_logger(__name__)

import simplejson
from z3c.saconfig import Session
from fernlehrgang import models
from datetime import datetime

class Worker(ConsumerMixin):

    _conn = None

    def __init__(self, connection, db, url):
        self.connection = connection
        self.zodb = db 
        self.url = url

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[vlw_queue, ],
                         accept=['pickle', 'json'],
                         callbacks=[self.run_task])]

    def run_task(self, body, message):
        connection = self.zodb.open()
        root = connection.root()
        try:
            with transaction.manager as tm:
                app = root['Application']['flg']
                setSite(app)
                import pdb; pdb.set_trace() 
                results = self.saveResult(body)
                results['kursteilnehmer_id'] = 900000
		newmessage = Message('results', data=results)
		with MQTransaction(self.url, QUEUES, transaction_manager=tm) as mqtm:
		    mqtm.createMessage(newmessage)
                message.ack()
        except StandardError, e:
            logger.error('task raised exception: %r', e)
            print e

    def saveResult(self, body):
        data = simplejson.loads(body)
        data['datum'] = datetime.now()
        data['system'] = "Virtuelle Lernwelt"
        session = Session()
        ktn = session.query(models.Kursteilnehmer).get(data.get('kursteilnehmer_id'))
        antwort = models.Antwort(**data)
        ktn.antworten.append(antwort)
        return ICalculateResults(ktn).summary()



ZOPE_CONF = "/home/vlw/fernlehrgang/parts/etc/zope.conf"
def main(url, conf):
    db = zope.app.wsgi.config(conf)
    with Connection(url) as conn:
        try:
            worker = Worker(conn, db, url)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')

