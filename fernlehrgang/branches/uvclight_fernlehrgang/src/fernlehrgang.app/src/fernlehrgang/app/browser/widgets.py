# -*- coding: utf-8 -*-

from cromlech.file import IFileField
from grokcore.chameleon.components import ChameleonPageTemplateFile
from grokcore.component import adapts, name
from zeam.form.base import interfaces
from zeam.form.base.interfaces import IFieldWidget
from zeam.form.base.widgets import DisplayFieldWidget
from zeam.form.ztk import customize
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField
from zeam.form.ztk.widgets.date import DateFieldWidget, DateFieldDisplayWidget
from zeam.form.ztk.widgets.text import TextSchemaField
from zope.component import getUtility
from zope.interface import Interface, implements
from zope.location import ILocation
from zope.schema.interfaces import IDate

from ..interfaces import IFrage
from ..wsgi import IFernlehrgangSkin


def register():
    """Entry point hook.
    """
    registerSchemaField(FileSchemaField, IFileField)


class IFileWidget(interfaces.IFieldWidget):
    """A widget that represents a file.
    """


class FileSchemaField(SchemaField):
    """A file field.
    """


class DisplaySQLImageWidget(DisplayFieldWidget):
    adapts(FileSchemaField, interfaces.IFormData, IFernlehrgangSkin)

    id = None
    url = None
    text = u''
    thumb = None
    template = ChameleonPageTemplateFile('templates/sqlimage.cpt')

    def update(self):
        DisplayFieldWidget.update(self)
        content = self.form.getContentData().getContent()
        if content:
            self.id = str(content.id)
            fileobj = self.component._field.get(content)
            if fileobj is not None:
                store = getUtility(Interface, name='ImageStore')
                self.text = (content.beschreibung.strip() or
                             u'<i>No description</i>')
                self.url = fileobj.locate(store=store)
                self.thumb = content.thumbnail.locate(store=store)


class SQLImageWidget(SchemaFieldWidget):
    adapts(FileSchemaField, interfaces.IFormData, IFernlehrgangSkin)

    id = None
    url = None
    text = u''
    thumb = None
    allow_action = False

    template = ChameleonPageTemplateFile('templates/sqlimage_edit.cpt')

    def update(self):
        SchemaFieldWidget.update(self)
        if not self.form.ignoreContent:
            content = self.form.getContentData().getContent()
            if content:
                self.id = str(content.id)
                fileobj = self.component._field.get(content)
                if fileobj is not None:
                    store = getUtility(Interface, name='ImageStore')
                    self.allow_action = True
                    self.text = (content.beschreibung.strip() or
                                 u'<i>No description</i>')
                    self.url = fileobj.locate(store=store)
                    self.thumb = content.thumbnail.locate(store=store)


class DisplayRichTextWidget(DisplayFieldWidget):
    adapts(TextSchemaField, interfaces.IFormData, IFernlehrgangSkin)
    name('richtext')
    template = None
    
    def render(self):
        DisplayFieldWidget.update(self)
        return self.value.get(self.identifier, u'')


@customize(origin=IDate)
def customize_size(field):
    field.valueLength = 'medium'


def fmtDate(d):
    return "%02d.%02d.%02d" % (d.day, d.month, d.year)


class DateFieldWidget(DateFieldWidget):

    def valueToUnicode(self, value):
        return fmtDate(value)


class DateFieldDisplayWidget(DateFieldDisplayWidget):

    def valueToUnicode(self, value):
        return fmtDate(value)
