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

        for lehrheft in context.lehrhefte:
            f_elem = SubElement(fernlehrgang, 'lehrheft')
            f_elem.attrib['lehrheft_id'] = str(notNone(lehrheft.id))
            


        return prettify(root)


