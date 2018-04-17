from unittest import TestCase
from os import path
import json
from fernlehrgang.api.gbo import GBOAPI


gboapi = GBOAPI()


class GBO_TEST(TestCase):

    def get_file(self, name):
        myfile = "%s/gbofiles/%s" % (path.dirname(__file__), name)
        return myfile

    def test_neusta_referenz(self):
        myfile = self.get_file('neusta_referenz.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_error_wrong_question_id(self):
        myfile = self.get_file('error_wrong_question_id.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_double_answer(self):
        myfile = self.get_file('double_answer.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_simple(self):
        myfile = self.get_file('basedoc_reduced.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 409)
        # Doppelter Benuztername
        myfile = self.get_file('existenter_benutzername.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_data_error_orgaids(self):
        """ Der Knotenname 'orgas' wurde in diesem Test falsch geschrieben """
        myfile = self.get_file('error_orgaids.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"Message":"The request is invalid.","ModelState":{"003":["All requested mappings cant be found and mapped."]}})

    def test_data_error_json(self):
        """ Der Knotenname 'orgas' wurde in diesem Test falsch geschrieben """
        myfile = self.get_file('error.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.text, u'{"Message":"The request is invalid.","ModelState":{"003":["All requested mappings cant be found and mapped."]}}')

    def test_fehler_in_mnr(self):
        myfile = self.get_file('error_mnr.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {u'ModelState': {u'importClientModel.Client.Number': [u"The field Number must be a string or array type with a minimum length of '9'.", u'The Number field is required.'], u'importClientModel.Client.MainNumber': [u'The MainNumber field is required.']}, u'Message': u'The request is invalid.'}) 
        myfile = self.get_file('error_mnrg9.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {u'ModelState': {u'importClientModel.Client.Number': [u"The field Number must be a string or array type with a maximum length of '9'.", u"The field Number must match the regular expression '^\\d{9,9}$'."]}, u'Message': u'The request is invalid.'})

    def test_fehler_in_email(self):
        #myfile = self.get_file('error_email.json')
        #with open(myfile, 'r') as fd:
        #    daten = json.load(fd)
        #    response = gboapi.set_data(daten)
        #    self.assertEqual(response.status_code, 400)
        #    print self.response.json()
        myfile = self.get_file('error_noemail.json')
        with open(myfile, 'r') as fd:
            daten = json.load(fd)
            response = gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {u'ModelState': {u'importClientModel.User.EMail': [u'The EMail field is required.']}, u'Message': u'The request is invalid.'})
