# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import grok
from xml.etree.cElementTree import ElementTree, Element, SubElement, tostring 
from zope.interface import Interface

from fernlehrgang.interfaces.flg import IFernlehrgang

class IXMLExport(Interface):
    """ xml export """

    def createXML():
        """ """

from xml.etree import ElementTree
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def notNone(value):
    """ Not None"""
    if value == None:
        return ''
    return value


class XMLExport(grok.Adapter):
    """ XML Export"""
    grok.implements(IXMLExport)
    grok.context(IFernlehrgang)

    def createXML(self):
        context = self.context

        root = Element("xml")
        lehrgaenge = SubElement(root, 'lehrgaenge')

        fernlehrgang = SubElement(lehrgaenge, 'fernlehrgang')
        fernlehrgang.attrib['flgid'] = str(notNone(context.id))
        fernlehrgang.attrib['titel'] = context.titel

        jahr = SubElement(fernlehrgang, 'jahr')
        jahr.text = str(context.jahr)

        # Zweig 1 Lehrhefte...

        for lehrheft in context.lehrhefte:
            l_elem = SubElement(fernlehrgang, 'lehrheft')
            l_elem.attrib['lehrheft_id'] = str(notNone(lehrheft.id))

            for frage in lehrheft.fragen:
                f_elem = SubElement(l_elem, 'frage')
                f_elem.attrib['frageid'] = str(notNone(frage.id))
                loesung = SubElement(f_elem, 'loesung')
                loesung.text = frage.antwortschema
                maxpunkte = SubElement(f_elem, 'maxpunkte')
                maxpunkte.text = str(frage.gewichtung)
            

        # Zweig 2 Kursteilnehmer...

        for kursteilnehmer in context.kursteilnehmer:
            teilnehmer = kursteilnehmer.teilnehmer
            k_elem = SubElement(fernlehrgang, 'kursteilnehmer')
            k_elem.attrib['ktlnid'] = str(notNone(kursteilnehmer.id))
            t_elem = SubElement(k_elem, 'teilnehmer')
            t_elem.attrib['tlnid'] = str(notNone(teilnehmer.id))

            #Personendaten
            SubElement(t_elem, 'anrede').text = teilnehmer.anrede
            SubElement(t_elem, 'titel').text = teilnehmer.titel
            SubElement(t_elem, 'name').text = teilnehmer.name
            SubElement(t_elem, 'vorname').text = teilnehmer.vorname
            SubElement(t_elem, 'gebdat').text = teilnehmer.geburtsdatum
            SubElement(t_elem, 'email').text = teilnehmer.email
            SubElement(t_elem, 'telpriv').text = ''
            SubElement(t_elem, 'teldienst').text = '' 
            SubElement(t_elem, 'telmobil').text = '' 
            SubElement(t_elem, 'telefax').text = ''

            #Unternehmen
            unternehmen = teilnehmer.unternehmen
            u_elem = SubElement(t_elem, 'unternehmen')
            u_elem.attrib['unternehmensid'] = unternehmen.mnr
            SubElement(u_elem, 'name1').text = unternehmen.name 
            SubElement(u_elem, 'name2').text = unternehmen.name2 
            SubElement(u_elem, 'name3').text = unternehmen.name3 
            SubElement(u_elem, 'strhnr').text = unternehmen.str
            SubElement(u_elem, 'plz').text = unternehmen.plz
            SubElement(u_elem, 'ort').text = unternehmen.ort

            #Versandanschrift
            v_elem = SubElement(t_elem, 'versandanschrift')
            SubElement(v_elem, 'name1').text = notNone(teilnehmer.anrede) + ' ' + notNone(teilnehmer.titel)
            SubElement(v_elem, 'name2').text = notNone(teilnehmer.name) + ' ' + notNone(teilnehmer.vorname)
            SubElement(v_elem, 'strhnr').text = notNone(teilnehmer.strasse) + ' ' + notNone(teilnehmer.nr)
            SubElement(v_elem, 'plz').text = teilnehmer.plz
            SubElement(v_elem, 'ort').text = teilnehmer.ort

            #Antworten
            a_elem = SubElement(t_elem, 'antworten')
            antworten = kursteilnehmer.antworten
            for antwort in antworten:
                an_elem = SubElement(a_elem, 'antwort')
                an_elem.attrib['antwortid'] = str(antwort.id)
                an_elem.attrib['lehrheftid'] = str(antwort.lehrheft_id) 
                an_elem.attrib['frageid'] = str(antwort.frage_id)
                SubElement(an_elem, 'loesung').text = notNone(antwort.antwortschema)
                SubElement(an_elem, 'maxpunkte').text = notNone(antwort.frage.gewichtung)


        return prettify(root)


