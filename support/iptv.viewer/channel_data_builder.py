#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'george'

import urllib2
import re
import os
import sys
from urlparse import urlparse
import json

sys.path.append(os.getcwd() + '/../../plugin.video.iptv.viewer')
from channel_cache import ChannelUrlCache, Channel, ChannelAdvancedSearch

class DataParser(ChannelUrlCache, ChannelAdvancedSearch):

    def getChannelsFromWeb(self):
        return None

    def __init__(self, path, data):
        self.run_data = data
        ChannelUrlCache.__init__(self, path, 'http://none', 5, data['output_name'])

    def get_channel_name(self, name, channels, append_string):
        saved_channel = self.getChannel(name, channels)
        if saved_channel is not None:
            if self.cleanString(saved_channel.name).split(' ') == self.cleanString(name).split(' '):
                if append_string is not None:
                    name = name + append_string
                    saved_channel = self.getChannel(name, channels)
                    if saved_channel is None or self.cleanString(saved_channel.name).split(' ') != self.cleanString(name).split(' '):
                        return name
                    else:
                        return None
                else:
                    return None
            else:
                return name
        else:
            return name

    def parse_url(self, main_url, channels, append_string = None):
        parts = urlparse(main_url)
        server_url = parts[0]+'://'+parts[1]

        url = urllib2.urlopen(main_url)
        data = url.readlines()
        url.close()
        regular = re.compile('.*<a class="b-link" href="(.+channel.+)">(.*)</a>')
        icon_regular = re.compile('.*<div class="b-channel-information__logo"><img.*?src="(.+?)".*')
        for line in data:
            u = unicode(line, 'utf8', 'ignore')
            for match in regular.finditer(u):
                print match.group(1)
                name = self.get_channel_name(match.group(2), channels, append_string)
                if name is not None:
                    url2 = urllib2.urlopen(server_url + match.group(1))
                    data2 = url2.readlines()
                    url2.close()
                    added = False
                    for line2 in data2:
                        u2 = unicode(line2, 'utf8', 'ignore')
                        match2 = icon_regular.search(u2)
                        if match2 is not None:
                            self.addNewChannel(Channel(name, match2.group(1), server_url + match.group(1)), channels)
                            added = True
                            del u2
                            break
                        del u2
                    del data2
                    if not added:
                        self.addNewChannel(Channel(name, None, server_url + match.group(1)), channels)
            del u
        del data

    def build_database(self):
        channels = {}
        urls = self.run_data['urls']
        for url in urls:
            self.parse_url(url['url'], channels, url['country_string'])
            self.setChannels(channels)

    def getChannelInfo(self, name):
        return self.getChannel(name, self.channels)

    def print_database(self):
        print self.channels


def  test(path, type):
    file = open(os.getcwd() + '/parser_urls.json')
    data = json.load(file)
    file.close()
    dp = DataParser(path, data[int(type)])
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


def run(out_path, file_id = None):
    file = open(os.getcwd() + '/parser_urls.json')
    data = json.load(file)
    file.close()

    if file_id is None:
        for d in data:
            DataParser(out_path, d).build_database()
    else:
        DataParser(out_path, data[int(file_id)]).build_database()


if __name__ == "__main__":
    path = os.getcwd() + '/db'
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            if len(sys.argv) > 2:
                test(path,sys.argv[2])
            else:
                test(path, 0)
        else:
            run(path, sys.argv[1])
    else:
        run(path)