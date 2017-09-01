from unittest import TestCase
from os import path
import json
from fernlehrgang.api.gbo import GBOAPI 


gboapi = GBOAPI()


class GBO_TEST(TestCase):

    def get_file(self, name):
        myfile = "%s/gbofiles/%s" % (path.dirname(__file__), name)
        return myfile

    def test_simple(self):
        myfile = self.get_file('basedoc.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, '201')
