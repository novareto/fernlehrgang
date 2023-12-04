from unittest import TestCase
from os import path
import json
from zope.app.appsetup import product

TOKEN = "772F0828-5EB3-4FAF-96C1-99A46A3D7F36"
URL = "https://gefaehrdungsbeurteilung-test-dmz-s1-nsd.neusta.de/data/flg/"


class GBO_TEST(TestCase):
    def setUp(self):
        product.setProductConfiguration("gbo", {"gbo_url": TOKEN, "gbo_token": URL})
        from fernlehrgang.api.gbo import GBOAPI

        self.gboapi = GBOAPI()

    def get_file(self, name):
        myfile = "%s/gbo_prod_files/%s" % (path.dirname(__file__), name)
        return myfile

    def test_neusta_referenz(self):
        """Test Gutfall, GBO soll sauber angelegt werden"""
        myfile = self.get_file("neusta_referenz.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_error_wrong_question_id(self):
        """Fehler im Mapping, Anlage erfolgt trotzdem"""
        myfile = self.get_file("error_wrong_question_id.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_double_answer(self):
        """Doppelte Frage, Anlage erfolgt trotzdem"""
        myfile = self.get_file("double_answer.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_ablauf(self):
        """Test Ablauf, 1. Anlage erfolgt. 2. Anlage ergibt den Status 409
        Doppleter Benutzername ist OK
        """
        myfile = self.get_file("basedoc_reduced.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)
            import time

            time.sleep(20)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 409)
        # Doppelter Benuztername
        myfile = self.get_file("existenter_benutzername.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 201)

    def test_data_error_orgaids(self):
        """Der Knotenname 'orgas' wurde in diesem Test falsch geschrieben"""
        myfile = self.get_file("error_orgaids.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)

    def test_data_error_json(self):
        """Fehlerhafter JSON Datenstream --> Keine Anlage"""
        myfile = self.get_file("error.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)

    def test_fehler_in_mnr(self):
        """Fehlerhafte Mitgliedsnummer --> Keine Anlage"""
        myfile = self.get_file("error_mnr.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
        myfile = self.get_file("error_mnrg9.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)

    def test_fehler_in_email(self):
        """Keine Mitgliedsnummer im Datensatz --> Keine Anlage"""
        myfile = self.get_file("error_noemail.json")
        with open(myfile, "r") as fd:
            daten = json.load(fd)
            response = self.gboapi.set_data(daten)
            self.assertEqual(response.status_code, 400)
