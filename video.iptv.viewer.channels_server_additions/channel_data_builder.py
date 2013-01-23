#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'george'

import urllib2
import re
import os
import sys
sys.path.append(os.getcwd() + '/../plugin.video.iptv.viewer')
from channel_cache import ChannelUrlCache, Channel, ChannelAdvancedSearch

class DataParser(ChannelUrlCache, ChannelAdvancedSearch):
    __server_url__ = "http://tv.yandex.ua"

    def getChannelsFromWeb(self):
        return None

    def __init__(self, path, filename = 'channels.ch'):
        ChannelUrlCache.__init__(self,path, 5, filename)

    def build_database(self):
        url = urllib2.urlopen(self.__server_url__ + '/187/channels')
        regular = re.compile('.*<a class="b-link" href="(.+channel.+)">(.*)</a>')
        icon_regular = re.compile('.*<div class="b-channel-information__logo"><img.*?src="(.+?)".*')
        channels = {}
        for line in url:
            u = unicode(line, 'utf8', 'ignore')
            for match in regular.finditer(u):
                url2 = urllib2.urlopen(self.__server_url__ + match.group(1))
                for line2 in url2:
                    u2 = unicode(line2, 'utf8', 'ignore')
                    match2 = icon_regular.search(u2)
                    if match2 is not None:
                        self.addNewChannel(Channel(match.group(2), match2.group(1), self.__server_url__ + match.group(1)), channels)
                        del u2
                        break
                    del u2
                url2.close()
            del u
        url.close()
        self.setChannels(channels)

    def getChannelInfo(self, name):
        return self.getChannel(name, self.channels)

    def print_database(self):
        print self.channels

if __name__ == "__main__":
    path = os.getcwd() + '/db'
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            dp = DataParser(path)
            dp.print_database()
            print '========================================'
            print dp.getChannelInfo(u'1+1')
            print dp.getChannelInfo(u'2+2')
            print dp.getChannelInfo(u'Discovery')
            print dp.getChannelInfo(u'Discovery World')
            print dp.getChannelInfo(u'Мега')
            print dp.getChannelInfo(u'ТРК Мега')
            print dp.getChannelInfo(u'ТК Мега')
            print dp.getChannelInfo(u'НТН')
        else:
            DataParser(path, sys.argv[1]).build_database()
    else:
        DataParser(path).build_database()