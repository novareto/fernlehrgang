# Package...

from redis import Redis
from rq import Queue
from rq.worker import SimpleWorker
from zope.app.wsgi import config

q = Queue(connection=Redis())


class ZCAWorker(SimpleWorker):

    def __init__(self, *args, **kwargs):
        super(ZCAWorker, self).__init__(*args, **kwargs)
        config('/Users/ck/work/bghw/new/fernlehrgang/parts/etc/zope.conf')


