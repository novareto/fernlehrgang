# -*- coding: utf-8 -*-
# Copyright (c) 2007-2016 NovaReto GmbH
# cklinger@novareto.de

import requests

data = {'teilnehmer_id': 100000}

URL = "http://localhost:8080/flg/%s"

result = requests.post(URL % 'getTeilnehmer', data=data)
print result.json()
print result.status_code


data = {
    'teilnehmer_id': 100000,
    'name': 'Callens',
    'vorname': 'Joris'}

result = requests.post(URL % 'setTeilnehmer', data=data)
print result.status_code
