#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'george'

import urllib2
import re
import os
import sys
from urlparse import urlparse
import json
import cookielib

sys.path.append(os.getcwd() + '/../../plugin.video.iptv.viewer')
from channel_cache import ChannelDataCache, Channel, ChannelAdvancedSearch


class DataParser(ChannelDataCache, ChannelAdvancedSearch):

    def getChannelsFromWeb(self):
        return self.channels

    def __init__(self, path, data):
        self.run_data = data
        ChannelDataCache.__init__(self, path, 'http://none', 10000000, data['output_name'])

    def parse_url(self, main_url, channels, append_string = None):
        parts = urlparse(main_url)
        server_url = parts[0]+'://'+parts[1]

        cookies = cookielib.FileCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        url = opener.open(main_url)
        data = url.readlines()
        url.close()

        regular = re.compile(
            '<a class="b-link.*?" href="([a-zA-Z0-9_\-/]+channels[a-zA-Z0-9_\-/]+)"><span.*?>'
            '<img.*?src="(.+?)".*?/span>(.*?)</a>',
            re.U
        )
        icon_regular = re.compile('<div class="b-tv-channel-content__channel-info"><span.*?><img.*?src="(.+?)"', re.U)
        for line in data:
            u = unicode(line, 'utf8', 'ignore')
            for match in regular.finditer(u):
                print match.group(3), " : ", match.group(1), " : ", match.group(2)
                name = self.cleanString(match.group(3), append_string)
                if name is not None:
                    url2 = opener.open(server_url + match.group(1))
                    data2 = url2.readlines()
                    url2.close()
                    added = False
                    for line2 in data2:
                        u2 = unicode(line2, 'utf8', 'ignore')
                        match2 = icon_regular.search(u2)
                        if match2 is not None:
                            print match2.group(1)
                            self.addNewChannel(Channel(name, match2.group(1), server_url + match.group(1)), channels)
                            added = True
                            del u2
                            break
                        del u2
                    del data2
                    if not added:
                        self.addNewChannel(Channel(name, match.group(2), server_url + match.group(1)), channels)
            del u
        del data

    def build_database(self):
        channels = set()
        urls = self.run_data['urls']
        for url in urls:
            self.parse_url(url['url'], channels, url['country_string'])
        self.setChannels(channels)

    def getChannelInfo(self, name):
        return self.getChannel(name, self.channels, u"украина")

    def print_database(self):
        for channel in self.channels:
         print channel


def test(path, type):
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
    print dp.getChannelInfo(u'Украина')
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
