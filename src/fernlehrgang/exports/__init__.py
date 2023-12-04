# Package...

from redis import Redis
from rq import Queue
from rq.worker import SimpleWorker
from megrok.nozodb.nozodb import config

q = Queue(connection=Redis())


class ZCAWorker(SimpleWorker):
    def __init__(self, *args, **kwargs):
        super(ZCAWorker, self).__init__(*args, **kwargs)
        config("/home/cklinger/work/bghw/flg/fernlehrgang/parts/etc/zope.conf")
