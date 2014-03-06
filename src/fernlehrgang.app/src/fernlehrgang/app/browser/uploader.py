# -*- coding: utf-8 -*-

import os
import shutil
import uvclight
from math import log

from dolmen.forms import crud
from dolmen.menu import menuentry
from dolmen.uploader.service import create_directory
from uvclight import Page
from uvclight.interfaces import IBelowContent

from zope.interface import implementer, Interface, Attribute
from zope.interface.common import mapping
from zope.location import locate
from zope.security.interfaces import Unauthorized
from zope.security.management import checkPermission

from ..wsgi import IFernlehrgangSkin
from .resources import upload
from .viewlets import NavigationMenu
from ..upload import IFileStore, IStorage, Storage, FileRepresentation

try:
    import cjson
    simple_jsonification = cjson.encode
except ImportError:
    import json
    simple_jsonification = json.dumps

    
SUFFIXES = u'b', u'Kb', u'Mb', u'Gb', u'Tb', u'Pb', u'Eb', u'Zb', u'Yb'
SIZE_SUFFIXES = [(s, float(2**(i*10))) for i, s in enumerate(SUFFIXES)]


def prettySize(size):
    """Pretty print file size for humans
    """
    if not size:
        return 'empty'
    size_type = int(log(size, 2) / 10)
    suf, lim = SIZE_SUFFIXES[size_type]
    return str(round(size/lim,2)) + suf

    
def format_file(url, file):
    return dict(
        name=file.filename,
        size=prettySize(file.size),
        url='%s/%s' % (url, file.id),
        delete_url='%s/%s' % (url, 'delete'),
        confirm_msg=u'Confirm deletion',
        delete_type='POST',
        )


class ReadWrapper(object):

    def __init__(self, f):
        self.close = f.close
        self._file = f

    def __iter__(self):
        f = self._file
        while 1:
            v = f.read(32768)
            if v:
                yield v
            else:
                break

            
class FilePublisher(uvclight.View):
    uvclight.name('index')
    uvclight.context(FileRepresentation)

    def update(self):
        """Sets the response headers, according to the data infos.
        """
        self.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % (self.context.filename))
        self.response.setHeader('Content-Length', self.context.size)

    def render(self):
        f = open(self.context.path, 'rb')
        return ReadWrapper(f)

    
class Upload(uvclight.View):
    uvclight.name('upload')
    uvclight.context(IStorage)

    def render(self):
        upload = self.request.form.get('file', None)
        if upload is not None:
            self.context[upload.filename] = upload
        files = [v.filename for v in self.context.values()]
        self.response.setHeader('Content-Type', "application/JSON")
        return simple_jsonification(files)


class FileManager(object):
    
    def format_file(self, file):
        return format_file(self.link, file, request=self.request)

    def POST(self):
        if 'file' in self.request.form:
            return self.delete()
        else:
            return self.add()

    def _delete(self):
        name = self.request.form.get('file', None)
        if name:
            file = self.context.get(file)
            response.write(simple_jsonification(
                format_file(self.link, file, request=self.request)))
            return response
        else:
            raise NotImplementedError('File %r does NOT exist.' % name)

    def _add(self):
        response = self.responseFactory()
        uploaded = self.request.form.get('uploader.file')

        filename = getattr(uploaded, 'filename', None)
        if filename:
            filename = clean_filename(filename)

        normalized_name = normalize_filename(filename)

        # no duplicate
        if (normalized_name in self.context or
            normalized_name + '.pdf' in self.context):
            response.write(simple_jsonification([
                {'error': translate(_(u'This file already exists'),
                                    context=self.request)}]))
            return response

        blob = AttachedFile(data=uploaded, filename=filename)
        name = NormalizingNamechooser(self.context).chooseName(
            normalized_name, blob)
        self.context[name] = blob

        response.write(simple_jsonification([
            format_file(self.link, blob, request=self.request)]))
        return response

    def GET(self):
        data = [format_file(self.link, f) for f in self.context.values()]
        return simple_jsonification(data)

    def render(self):
        pass


@menuentry(NavigationMenu, order=10)
class LibraryListing(uvclight.Page):
    uvclight.name('files')
    uvclight.title('Download Center')
    uvclight.context(IFileStore)
    template = uvclight.get_template('librarylisting.cpt', __file__) 

    def update(self):
        storage = Storage(self.context.storageid)
        locate(storage, self.context, '++storage++')
        storage_url = self.url(storage)
        self.files = [format_file(storage_url, f) for f in storage.values()]


class LibraryUploadViewlet(uvclight.Viewlet):
    uvclight.name('files')
    uvclight.view(LibraryListing)
    uvclight.layer(IFernlehrgangSkin)
    uvclight.viewletmanager(IBelowContent)
    uvclight.context(IFileStore)
    template = uvclight.get_template('libraryuploadviewlet.cpt', __file__)
    
    def update(self, *args, **kwargs):
        upload.need()
        uvclight.Viewlet.update(self)
        storage = Storage(self.context.storageid)
        locate(storage, self.context, '++storage++')
        storage_url = self.view.url(storage)
        self.action = storage_url + "/upload"
        self.files = [format_file(storage_url, f) for f in storage.values()]
        self.upload_title = u"Attach files"


