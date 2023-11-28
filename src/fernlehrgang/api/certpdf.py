# -*- coding: utf-8 -*-
# Import der benoetigten Bibliotheken
import pathlib
import fernlehrgang.api

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from time import strftime, gmtime



# Definition einer Funktion
def createpdf(filehandle, data):
    """
    Schreibt eine PDF-Datei
    """

    # Pfad und Dateiname
    # c ist ein Objekt der Klasse Canvas
    image = pathlib.Path(fernlehrgang.api.__file__).resolve().parent / "FLG_Bescheinigung_Ansicht_Image.jpg"
    c = canvas.Canvas(filehandle, pagesize=A4)

    # Metainformationen fuer das PDF-Dokument
    c.setAuthor(u"Berufsgenossenschaft Handel und Warenlogistik")
    c.setTitle(u"Teilnahmezertifikat Fernlehrgang")

    # Variablen
    schriftart = "Helvetica"
    schriftartfett = "Helvetica-Bold"
    datum = strftime("%d.%m.%Y",gmtime())

    anrede = {"1": "Herr", "2": "Frau"}
    titel = {"0": "", "1": "Dr.", "2": "Prof."}

    c.drawImage(image, 0 * cm, 0 * cm, width=20.993 * cm, height=29.693 * cm)

    c.setFont(schriftart, 12)
    c.drawString(13.8 * cm, 23.52 * cm, data.get("flg_titel", u" "))
    c.drawString(13.8 * cm, 22.92 * cm, u"Benutzer-Nr.: %s " % data.get("teilnehmer_id", u" "))

    fullname = "%s %s %s %s" % (
        anrede[data.get("anrede", "1")],
        titel[data.get("titel", u"0")],
        data.get("vorname"),
        data.get("name"),
    )

    c.setFont(schriftartfett, 20)
    c.drawString(2.15 * cm, 18 * cm, ' '.join(fullname.split(' ')).strip())

    c.setFont(schriftart, 12)
    from datetime import datetime
    import locale
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    try:
        dd = datetime.strptime(data.get("druckdatum"), '%d.%m.%Y').strftime('Bonn, %d. %B %Y')
    except:
        dd = data.get("druckdatum")
    c.drawString(2.15 * cm, 5.5 * cm, dd)
    c.showPage()
    c.save()
    return filehandle


def createfortpdf(filehandle, data):
    """
    Schreibt eine PDF-Datei
    """

    #Pfad und Dateiname
    image = pathlib.Path(fernlehrgang.api.__file__).resolve().parent / "FLG_Fortbildung_Ansicht_Image.jpg"
    timestamp=strftime("%d%m%Y%H%M%S",gmtime()) #Ermitteln der aktuellen Uhrzeit und Formatierung eines Strings mit Zeitstempel
    dateiname = "/tmp/%s_certificate.pdf" %data.get('mnr','')

    #c ist ein Objekt der Klasse Canvas
    c = canvas.Canvas(filehandle,pagesize=A4)

    #Metainformationen fuer das PDF-Dokument
    c.setAuthor(u"Berufsgenossenschaft Handel und Warenlogistik")
    c.setTitle(u"Teilnahmezertifikat Fernlehrgang")

    #Variablen
    schriftart = "Helvetica"
    schriftartfett = "Helvetica-Bold"
    datum = strftime("%d.%m.%Y",gmtime())

    anrede = {'0': '', '1':'Herr', '2':'Frau'}
    titel = {'0': '', '1': 'Dr.', '2': 'Prof.'}

    c.drawImage(image, 0*cm, 0*cm, width=20.993*cm, height=29.693*cm)


    c.setFont(schriftartfett,12)
    c.drawString(14.6*cm, 23.6*cm, data.get('flg_titel', u' '))
    c.drawString(14.6*cm, 23.0*cm, u'Benutzer-Nr.: %s' % data.get('teilnehmer_id',u' '))
    c.setFont(schriftart,10)
    fullname = "%s %s %s %s" %(anrede[data.get('anrede', '1')],
                               titel[data.get('titel',u'0')],
                               data.get('vorname'),
                               data.get('name'),)

    c.setFont(schriftartfett, 20)
    c.drawString(2.15*cm, 18*cm, ' '.join(fullname.split(' ')).strip())

    c.setFont(schriftart, 12)
    c.drawString(2.2*cm, 5.5*cm, u"Bonn, %s" %data.get('certdatum'))

    c.showPage()
    c.save()
    return filehandle
