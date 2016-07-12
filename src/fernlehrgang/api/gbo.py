import json
import requests


TESTJSON = {
        "token": "772F0828-5EB3-4FAF-96C1-99A46A3D7F36",
        "client": {
            "number": "123456789",
            "mainnumber": "123456789",
            "name": "Beispielbetrieb GmbH",
            "zip": "53113",
            "city": "Bonn",
            "street": "Beispielstrasse 5",
            "compcenter": 1
            },
        "user": {
            "login": "wtestuser",
            "salutation": 1,
            "title": "Dr.",
            "firstname": "Wilhelm",
            "lastname": "Brause",
            "phone": "02323-23232",
            "email": "a.tkacuk@neusta.de"
            },
        "orgas": [
            {
                "id": 1,
                "answers": [
                    {
                        "questionid": 1,
                        "answer": "Ja"
                        },
                    {
                        "questionid": 2,
                        "answer": 3
                        },
                    {
                        "questionid": 3,
                        "answer": 3
                        }
                    ]
                },
            {
                "id": 2,
                "answers": [
                    {
                        "questionid": 1,
                        "answer": 1
                        },
                    {
                        "questionid": 2,
                        "answer": 1
                        },
                    {
                        "questionid": 3,
                        "answer": 3
                        }
                    ]
                }
            ]
        }


class GBOAPI(object):
    url = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/beta/flg"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        }

    def get_info(self, mnr):
        url = "%s/import/clients/%s/info" % (self.url, mnr)
        r = requests.get(url, headers=self.headers)
        return r

    def set_data(self, data):
        url = "%s/import/clients" % self.url
        r = requests.post(
            url, 
            json=TESTJSON, 
            headers=self.headers
        )
        return r


gboapi = GBOAPI()

t = gboapi.get_info('123456789')
t = gboapi.get_info('888899998')
print gboapi.set_data(TESTJSON)
