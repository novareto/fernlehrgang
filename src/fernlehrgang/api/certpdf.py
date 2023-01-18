# -*- coding: utf-8 -*-
# Import der benoetigten Bibliotheken
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from time import strftime, gmtime


image = "/home/bghw/fernlehrgang/parts/omelette/fernlehrgang/api/FLG_Bescheinigung_Ansicht_Image.jpg"


# Definition einer Funktion
def createpdf(filehandle, data):
    """
    Schreibt eine PDF-Datei
    """

    # Pfad und Dateiname
    # c ist ein Objekt der Klasse Canvas
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
    #c.drawString(14 * cm, 20.5 * cm, u"FLG-ID:")
    #c.drawString(14 * cm, 20 * cm, u"Mitgl.-Nr.:")
    #c.drawRightString(20 * cm, 22.92 * cm, data.get("teilnehmer_id", u" "))
    #c.drawRightString(20 * cm, 20.5 * cm, data.get("flg_id", u" "))
    #c.drawRightString(20 * cm, 20 * cm, data.get("mnr", u" "))

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
