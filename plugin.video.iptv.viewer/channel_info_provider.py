#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'george'

import os
#import base64
from channel_cache import ChannelDataCache, ChannelAdvancedSearch

class InfoProvider(ChannelDataCache, ChannelAdvancedSearch):

    def __init__(self, path, update_url, country_string = None):
        self.country_string = country_string
        ChannelDataCache.__init__(self, path, update_url, 300000)

    def getChannelInfo(self, channel_name):
        channel = self.getChannel(channel_name, self.channels, self.country_string)
        return None if channel is None else channel.info_url

    def getImageURL(self, channel_name):
        channel = self.getChannel(channel_name, self.channels, self.country_string)
        return None if channel is None else channel.image_url

#    def getURL(self, key):
#        channel = self.getChannel(key, self.channels, self.country_string)
#        return None if channel is None else channel.image_url

#    def getFileItemName(self, key):
 #       return base64.urlsafe_b64encode(key.encode('utf-8')) + '.png'

if __name__ == '__main__':
    provider = InfoProvider(os.getcwd() + '/temp_cache', 'https://dl.dropbox.com/s/284qhw5g7dovpl7/channels.ch?dl=1')
    try:
        print '1+1', provider.getImageURL("1+1")
    except KeyError:
        pass
    try:
        print '2+2', provider.getImageURL("2+2")
    except KeyError:
        pass
    try:
        print 'Discovery', provider.getImageURL("Discovery")
    except KeyError:
        pass
    try:
        print 'HTH', provider.getImageURL(u"НТН")
    except KeyError:
        pass
    print 'MAIN FINISHED'
