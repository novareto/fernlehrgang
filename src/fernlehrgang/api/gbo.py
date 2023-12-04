# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import json
import requests


from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from zope.app.appsetup.product import getProductConfiguration
from fernlehrgang.api.testdata import PRODJSON, TESTJSON
from fernlehrgang.api.gbo_base_calls import set_it, get_it, success as report_success
from fernlehrgang.exports import q


config = getProductConfiguration("gbo")
GBO_URL = config.get("gbo_url")


class GBOAPI(object):
    url = GBO_URL
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-agent": "Mozilla/5.0",
    }


    def get_info(self, mnr):
        url = "%s/import/clients/%s/info" % (self.url, mnr)
        r = requests.get(url, headers=self.headers)
        #r = q.enqueue(get_it, args=(url, self.headers), description = 'GET INFO %s' % mnr, on_success=report_success)
        return r

    def set_data(self, data):
        url = "%simport/clients" % self.url
        r = q.enqueue(set_it, args = (url, data, self.headers))
        print(r.text)
        return r


GBO_URL = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"
GBO_URL = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"


if __name__ == "__main__":
    gboapi = GBOAPI()
    gboapi.url = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"

    t = gboapi.get_info("995000102")
    print(t)
    # t = gboapi.get_info('100000020')

    #
    #    import httplib as http_client
    #    http_client.HTTPConnection.debuglevel = 1
    #
    ## You must initialize logging, otherwise you'll not see debug output.
    #    logging.basicConfig()
    #    logging.getLogger().setLevel(logging.DEBUG)
    #    requests_log = logging.getLogger("requests.packages.urllib3")
    #    requests_log.setLevel(logging.DEBUG)
    #    requests_log.propagate = True

    # import httplib as http_client

    # http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    #logging.basicConfig()
    #logging.getLogger().setLevel(logging.DEBUG)
    #requests_log = logging.getLogger("requests.packages.urllib3")
    #requests_log.setLevel(logging.DEBUG)
    #requests_log.propagate = True

    #t = gboapi.set_data(json.loads(PRODJSON))
