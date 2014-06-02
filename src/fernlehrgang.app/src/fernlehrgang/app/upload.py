# -*- coding: utf-8 -*-

import os
import base64
import shutil

from dolmen.uploader.service import create_directory
from zope.interface import implementer, Interface, Attribute
from zope.interface.common import mapping
from zope.location import Location


class IFileStore(Interface):
    """Interface for items that can be a file store.
    """
    storageid = Attribute('ID of the storage')
    

class IStorage(mapping.IReadMapping, mapping.IWriteMapping):

    id = Attribute('ID of the storage')


class FileRepresentation(Location):

    def __init__(self, path, id, filename, size):
        self.id = id
        self.path = path
        self.filename = filename
        self.size = size

    def delete(self):
        os.remove(self.path)


def map_folder(root, decode=None):
    datas = {}
    files = os.listdir(root)
    for f in files:
        path = os.path.join(root, f)
        if os.path.isdir(path):
            continue
        else:
            stats = os.stat(path)
            if decode is not None:
                filename = decode(f.encode("utf-8"))
            else:
                filename = f
            datas[f] = FileRepresentation(path, f, filename, stats.st_size)
    return datas

        
@implementer(IStorage)
class Storage(Location):

    datas = dict()

    @staticmethod
    def encode(value):
        return base64.urlsafe_b64encode(value)

    @staticmethod
    def decode(value):
        return base64.urlsafe_b64decode(value)
    
    def __init__(self, id, root="/home/novareto/fernlehrgang/uvclight"):
        self.id = id

        storage = create_directory(os.path.join(root, id))

        if storage is None:
            raise RuntimeError(os.path.join(root, id))
    
        self.storage = storage
        self.refresh()

    def refresh(self):
        self.datas = map_folder(self.storage, decode=base64.urlsafe_b64decode)

    def __getitem__(self, name):
        return self.datas.__getitem__(name)

    def get(self, name, default=None):
        return self.datas.get(name, default)

    def keys(self):
        return self.datas.keys()

    def __iter__(self):
        return iter(self.datas)

    def values(self):
        return self.datas.values()

    def items(self):
        return self.datas.items()

    def __len__(self):
        return len(self.datas)

    def __delitem__(self, key):
        item = self.datas.get(key)
        if item is None:
            raise KeyError

        item.delete()
        self.datas.__delitem__(key)
        self.refresh()

    def __setitem__(self, key, value):
        k = self.encode(key)
        if k in self.datas:
            raise KeyError
        path = os.path.join(self.storage, k)        
        with open(path, 'w') as upload:
            shutil.copyfileobj(value, upload)
        self.refresh()

    def traverse(self, name):
        return self.get(name)
