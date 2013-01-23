# -*- coding: utf-8 -*-
__author__ = 'george'

import os
import urllib2
import pickle
import time
import shutil

class File(object):
    def __init__(self, path, create_time = None):
        self.path = path
        self.time = time.time() if create_time is None else create_time

    def __str__(self):
        return "File: " + self.path

    def life_time(self):
        return time.time() - self.time


class FileCache(object):
    def __init__(self, path):
        self.cache_path = path
        self.cache_file = os.path.join(path, 'cache.ch')
        self.cache_time = 32000

        try:
            file = open(self.cache_file, 'rt')
            self.data = pickle.load(file)
            file.close()
            self.clear_deleted()
        except IOError:
            self.data = {}
            shutil.rmtree(self.cache_path)
            os.mkdir(self.cache_path)
            self.save()

    def clear_deleted(self):
        files = []
        remove_keys = []
        for key, val in self.data.items():
            if val.life_time() > self.cache_time:
                remove_keys.append(key)
            else:
                files.append(os.path.basename(val.path))

        for key in remove_keys:
            del self.data[key]

        cache = os.listdir(self.cache_path)
        for f in cache:
            if f[-3:] != '.ch' and f not in files:
                os.remove(os.path.join(self.cache_path, f))

    def save(self):
        fd = open(self.cache_file, 'wt')
        pickle.dump(self.data, fd)
        fd.close()

    def getURL(self, key):
        assert "Must be implemented in subclass"

    def getFileItemName(self, key):
        assert "Must be implemented in subclass"

    def updateCacheItem(self, key):
        url = self.getURL(key)
        if url is not None:
            try:
                file = self.data[key]
                os.remove(file)
            except KeyError:
                pass
            fd = urllib2.urlopen(url)
            file = os.path.join(self.cache_path, self.getFileItemName(key))
            fd2 = open(file, 'wb')
            fd2.write(fd.read())
            fd.close()
            fd2.close()
            self.data[key] = File(file)
            self.save()

    def getFilePath(self, key):
        try:
            file = self.data[key]
        except KeyError:
            self.updateCacheItem(key)
            file = self.data[key]
        if file.life_time() > self.cache_time:
            self.updateCacheItem(key)
            file = self.data[key]
        return file.path
