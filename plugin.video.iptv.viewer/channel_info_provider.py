#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'george'

import os
import cache
import base64
from channel_cache import ChannelUrlCache, ChannelAdvancedSearch

class InfoProvider(cache.FileCache, ChannelUrlCache, ChannelAdvancedSearch):

    def __init__(self, path, update_url):
        super(InfoProvider, self).__init__(path)
        self.cache_time = 300000
        self.can_update = True
        ChannelUrlCache.__init__(self, path, update_url, self.cache_time)

    def getInfo(self, key):
        channel = self.getChannel(key, self.channels)
        return None if channel is None else channel.info_url

    def getURL(self, key):
        channel = self.getChannel(key, self.channels)
        return None if channel is None else channel.image_url

    def getFileItemName(self, key):
        return base64.urlsafe_b64encode(key.encode('utf-8')) + '.png'

if __name__ == '__main__':
    provider = InfoProvider(os.getcwd() + '/temp_cache', 'https://dl.dropbox.com/s/284qhw5g7dovpl7/channels.ch?dl=1')
    try:
        print '1+1', provider.getFilePath("1+1")
    except KeyError:
        pass
    try:
        print '2+2', provider.getFilePath("2+2")
    except KeyError:
        pass
    try:
        print 'Discovery', provider.getFilePath("Discovery")
    except KeyError:
        pass
    try:
        print 'HTH', provider.getFilePath(u"НТН")
    except KeyError:
        pass
    print 'MAIN FINISHED'
