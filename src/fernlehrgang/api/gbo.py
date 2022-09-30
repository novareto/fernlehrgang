# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import json
import requests
from zope.app.appsetup.product import getProductConfiguration

#config = getProductConfiguration("gbo")
#GBO_URL = config.get("gbo_url")

GBO_URL = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"
GBO_URL = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"
PRODJSON = u"""{
  "token": "772F0828-5EB3-4FAF-96C1-99A46A3D7F36",
  "client": {
    "number": "111222444",
    "mainnumber": "111222444",
    "name": "FLG-Test novareto über Request",
    "zip": "28888",
    "city": "Woauchimmer",
    "street": "Alte Reihe 188",
    "compcenter": 0
  },
  "user": {
    "login": "flgnovareto",
    "salutation": 1,
    "title": "Dr.",
    "firstname": "Norbert",
    "lastname": "FLG-Novareto",
    "phone": "04408-22222",
    "email": "cklinger@novareto.de"
  },
  "orgas": [
    {
      "id": 1,
      "answers": [
          {"questionid":2000, "answer":1},
          {"questionid":2001, "answer":1},
          {"questionid":2002, "answer":1},
          {"questionid":2003, "answer":1},
          {"questionid":2005, "answer":1},
          {"questionid":2006, "answer":1},
          {"questionid":2007, "answer":1},
          {"questionid":2008, "answer":1},
          {"questionid":2010, "answer":1},
          {"questionid":2011, "answer":1},
          {"questionid":2012, "answer":1},
          {"questionid":2013, "answer":1},
          {"questionid":2014, "answer":1},
          {"questionid":2015, "answer":1},
          {"questionid":2016, "answer":1},
          {"questionid":2017, "answer":1},
          {"questionid":2018, "answer":1}
       ]
    },
    {
      "id": 2,
      "answers": [
        {"questionid":1000, "answer":1},
        {"questionid":1001, "answer":1},
        {"questionid":1002, "answer":1},
        {"questionid":1003, "answer":1},
        {"questionid":1004, "answer":1},
        {"questionid":1005, "answer":1},
        {"questionid":1006, "answer":1},
        {"questionid":1007, "answer":1},
        {"questionid":1008, "answer":1},
        {"questionid":1009, "answer":1},
        {"questionid":1010, "answer":1},
        {"questionid":1011, "answer":1},
        {"questionid":1012, "answer":1},
        {"questionid":1013, "answer":1},
        {"questionid":1014, "answer":1},
        {"questionid":1017, "answer":1},
        {"questionid":1023, "answer":1},
        {"questionid":1024, "answer":1},
        {"questionid":1025, "answer":1},
        {"questionid":1026, "answer":1},
        {"questionid":1027, "answer":1},
        {"questionid":1028, "answer":1},
        {"questionid":1029, "answer":1},
        {"questionid":1031, "answer":1},
        {"questionid":1032, "answer":1},
        {"questionid":1046, "answer":1},
        {"questionid":1047, "answer":1},
        {"questionid":1050, "answer":1},
        {"questionid":1051, "answer":1},
        {"questionid":1052, "answer":1},
        {"questionid":1058, "answer":1},
        {"questionid":1059, "answer":1},
        {"questionid":1060, "answer":1},
        {"questionid":1061, "answer":1},
        {"questionid":1062, "answer":1},
        {"questionid":1063, "answer":1},
        {"questionid":1064, "answer":1},
        {"questionid":1067, "answer":1},
        {"questionid":1068, "answer":1},
        {"questionid":1069, "answer":1},
        {"questionid":1070, "answer":1},
        {"questionid":1071, "answer":1},
        {"questionid":1074, "answer":1},
        {"questionid":1075, "answer":1},
        {"questionid":1076, "answer":1},
        {"questionid":1082, "answer":1},
        {"questionid":1084, "answer":1},
        {"questionid":4017, "answer":1},
        {"questionid":4018, "answer":1},
        {"questionid":4019, "answer":1},
        {"questionid":4020, "answer":1},
        {"questionid":4021, "answer":1},
        {"questionid":4022, "answer":1},
        {"questionid":4004, "answer":1},
        {"questionid":4005, "answer":1},
        {"questionid":4006, "answer":1},
        {"questionid":4007, "answer":1},
        {"questionid":4008, "answer":1},
        {"questionid":4009, "answer":1}
      ]
    },
    {
      "id":3,
      "answers": [
        {"questionid":3002, "answer":1},
        {"questionid":3003, "answer":1},
        {"questionid":3004, "answer":1},
        {"questionid":3005, "answer":1},
        {"questionid":3006, "answer":1},
        {"questionid":3007, "answer":1},
        {"questionid":3008, "answer":1},
        {"questionid":3009, "answer":1},
        {"questionid":3015, "answer":1},
        {"questionid":3016, "answer":1},
        {"questionid":3021, "answer":1},
        {"questionid":3022, "answer":1},
        {"questionid":3023, "answer":1},
        {"questionid":3027, "answer":1}
      ]
    },
    {
      "id": 4,
      "answers": [
        {"questionid":4001, "answer":1},
        {"questionid":4010, "answer":1},
        {"questionid":4011, "answer":1},
        {"questionid":4012, "answer":1},
        {"questionid":4015, "answer":1},
        {"questionid":4024, "answer":1},
        {"questionid":4025, "answer":1},
        {"questionid":4026, "answer":1},
        {"questionid":4027, "answer":1},
        {"questionid":4028, "answer":1},
        {"questionid":4029, "answer":1},
        {"questionid":4030, "answer":1},
        {"questionid":4031, "answer":1},
        {"questionid":4038, "answer":1}
      ]
   }
  ]
}"""

TESTJSON = u"""{
"token": "772F0828-5EB3-4FAF-96C1-99A46A3D7F36",
  "client": {
    "number": "100000020",
    "mainnumber": "100000000",
    "name": "FLG-Mappingtest komplett (2)",
    "zip": "27343",
    "city": "Irgendwo",
    "street": "Betriebsstrasse 188",
    "compcenter": 0
  },
  "user": {
    "login": "flgtest1",
    "salutation": 1,
    "title": "Dr.",
    "firstname": "Fritz",
    "lastname": "Klinger",
    "phone": "04408-786",
    "email": "c.fleuter@neusta.de"
  },
  "orgas": [
    {
      "id": 1,
      "answers": [
        {"questionid":2000, "answer":1},
        {"questionid":2001, "answer":4},
        {"questionid":2002, "answer":5},
        {"questionid":2003, "answer":3},
        {"questionid":2005, "answer":1},
        {"questionid":2006, "answer":1},
        {"questionid":2007, "answer":1},
        {"questionid":2008, "answer":1},
        {"questionid":2009, "answer":1},
        {"questionid":2010, "answer":4},
        {"questionid":2011, "answer":4},
        {"questionid":2012, "answer":1},
        {"questionid":2013, "answer":1},
        {"questionid":2014, "answer":1},
        {"questionid":2015, "answer":5},
        {"questionid":2016, "answer":1},
        {"questionid":2017, "answer":5},
        {"questionid":2018, "answer":1}
      ]
    },
    {
      "id": 2,
      "answers": [
        {"questionid":1000, "answer":4},
        {"questionid":1001, "answer":5},
        {"questionid":1002, "answer":1},
        {"questionid":1003, "answer":1},
        {"questionid":1004, "answer":1},
        {"questionid":1005, "answer":1},
        {"questionid":1006, "answer":3},
        {"questionid":1007, "answer":1},
        {"questionid":1008, "answer":1},
        {"questionid":1009, "answer":1},
        {"questionid":1010, "answer":1},
        {"questionid":1011, "answer":1},
        {"questionid":1012, "answer":4},
        {"questionid":1013, "answer":1},
        {"questionid":1014, "answer":4},
        {"questionid":1015, "answer":1},
        {"questionid":1016, "answer":1},
        {"questionid":1017, "answer":1},
        {"questionid":1019, "answer":1},
        {"questionid":1020, "answer":1},
        {"questionid":1021, "answer":1},
        {"questionid":1022, "answer":1},
        {"questionid":1023, "answer":1},
        {"questionid":1024, "answer":1},
        {"questionid":1025, "answer":1},
        {"questionid":1026, "answer":1},
        {"questionid":1027, "answer":1},
        {"questionid":1028, "answer":1},
        {"questionid":1029, "answer":5},
        {"questionid":1030, "answer":5},
        {"questionid":1031, "answer":1},
        {"questionid":1032, "answer":1},
        {"questionid":1033, "answer":1},
        {"questionid":1034, "answer":1},
        {"questionid":1035, "answer":1},
        {"questionid":1036, "answer":1},
        {"questionid":1037, "answer":1},
        {"questionid":1038, "answer":1},
        {"questionid":1039, "answer":1},
        {"questionid":1040, "answer":1},
        {"questionid":1041, "answer":1},
        {"questionid":1042, "answer":1},
        {"questionid":1043, "answer":1},
        {"questionid":1044, "answer":1},
        {"questionid":1045, "answer":1},
        {"questionid":1046, "answer":1},
        {"questionid":1047, "answer":1},
        {"questionid":1048, "answer":1},
        {"questionid":1049, "answer":1},
        {"questionid":1050, "answer":1},
        {"questionid":1051, "answer":1},
        {"questionid":1052, "answer":1},
        {"questionid":1053, "answer":1},
        {"questionid":1054, "answer":1},
        {"questionid":1055, "answer":1},
        {"questionid":1056, "answer":1},
        {"questionid":1057, "answer":1},
        {"questionid":1058, "answer":1},
        {"questionid":1059, "answer":1},
        {"questionid":1060, "answer":1},
        {"questionid":1061, "answer":1},
        {"questionid":1062, "answer":1},
        {"questionid":1063, "answer":1},
        {"questionid":1064, "answer":1},
        {"questionid":1067, "answer":3},
        {"questionid":1068, "answer":3},
        {"questionid":1069, "answer":1},
        {"questionid":1070, "answer":5},
        {"questionid":1071, "answer":1},
        {"questionid":1072, "answer":4},
        {"questionid":1073, "answer":1},
        {"questionid":1074, "answer":1},
        {"questionid":1075, "answer":1},
        {"questionid":1076, "answer":1},
        {"questionid":1077, "answer":1},
        {"questionid":1078, "answer":1},
        {"questionid":1079, "answer":1},
        {"questionid":1080, "answer":1},
        {"questionid":1081, "answer":1},
        {"questionid":1082, "answer":1},
        {"questionid":1083, "answer":1},
        {"questionid":1084, "answer":1},
        {"questionid":1085, "answer":1},
        {"questionid":4017, "answer":1},
        {"questionid":4018, "answer":1},
        {"questionid":4019, "answer":1},
        {"questionid":4020, "answer":1},
        {"questionid":4021, "answer":1},
        {"questionid":4022, "answer":1},
        {"questionid":4007, "answer":1},
        {"questionid":4008, "answer":1},
        {"questionid":4009, "answer":1},
        {"questionid":4010, "answer":1},
        {"questionid":4011, "answer":1},
        {"questionid":4012, "answer":4}
      ]
    },
    {
      "id":3,
      "answers": [
        {"questionid":3000, "answer":3},
        {"questionid":3001, "answer":1},
        {"questionid":3002, "answer":4},
        {"questionid":3003, "answer":1},
        {"questionid":3004, "answer":1},
        {"questionid":3005, "answer":1},
        {"questionid":3006, "answer":5},
        {"questionid":3007, "answer":1},
        {"questionid":3008, "answer":1},
        {"questionid":3009, "answer":1},
        {"questionid":3010, "answer":1},
        {"questionid":3011, "answer":1},
        {"questionid":3012, "answer":1},
        {"questionid":3013, "answer":1},
        {"questionid":3014, "answer":1},
        {"questionid":3015, "answer":1},
        {"questionid":3016, "answer":1},
        {"questionid":3017, "answer":1},
        {"questionid":3018, "answer":1},
        {"questionid":3019, "answer":1},
        {"questionid":3020, "answer":1},
        {"questionid":3021, "answer":1},
        {"questionid":3022, "answer":1},
        {"questionid":3023, "answer":1},
        {"questionid":3024, "answer":1},
        {"questionid":3025, "answer":4},
        {"questionid":3026, "answer":4},
        {"questionid":3027, "answer":1},
        {"questionid":3028, "answer":5},
        {"questionid":3029, "answer":1},
        {"questionid":3030, "answer":1},
        {"questionid":3031, "answer":1},
        {"questionid":3032, "answer":1},
        {"questionid":3033, "answer":1},
        {"questionid":3034, "answer":1},
        {"questionid":3035, "answer":1},
        {"questionid":3036, "answer":1},
        {"questionid":3037, "answer":1},
        {"questionid":3039, "answer":1}
      ]
    },
   {
      "id": 4,
      "answers": [
        {"questionid":4000, "answer":1},
        {"questionid":4001, "answer":1},
        {"questionid":4002, "answer":1},
        {"questionid":4003, "answer":1},
        {"questionid":4010, "answer":1},
        {"questionid":4011, "answer":1},
        {"questionid":4012, "answer":1},
        {"questionid":4013, "answer":1},
        {"questionid":4014, "answer":1},
        {"questionid":4015, "answer":1},
        {"questionid":4016, "answer":1},
        {"questionid":4023, "answer":1},
        {"questionid":4024, "answer":1},
        {"questionid":4025, "answer":1},
        {"questionid":4026, "answer":1},
        {"questionid":4027, "answer":1},
        {"questionid":4028, "answer":1},
        {"questionid":4029, "answer":1},
        {"questionid":4030, "answer":1},
        {"questionid":4031, "answer":1},
        {"questionid":4032, "answer":1},
        {"questionid":4033, "answer":1},
        {"questionid":4034, "answer":1},
        {"questionid":4035, "answer":1},
        {"questionid":4036, "answer":1},
        {"questionid":4037, "answer":1},
        {"questionid":4038, "answer":1},
        {"questionid":4039, "answer":1},
        {"questionid":4040, "answer":1}
         ]
    }

  ]
}
"""


class GBOAPI(object):
    url = GBO_URL
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def get_info(self, mnr):
        url = "%s/import/clients/%s/info" % (self.url, mnr)
        r = requests.get(url, headers=self.headers)
        return r

    def set_data(self, data):
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        url = "%simport/clients" % self.url
        print(url)
        r = session.post(
            url,
            json=data,
            headers=self.headers
        )
        #r = requests.post(url, json=data, headers=self.headers)
        return r


if __name__ == "__main__":
    gboapi = GBOAPI()
    gboapi.url =  "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"

    t = gboapi.get_info("995000102")
    import pdb; pdb.set_trace()
    print(t)
    # t = gboapi.get_info('100000020')

    import logging
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

    #import httplib as http_client

    #http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    t = gboapi.set_data(json.loads(PRODJSON))
