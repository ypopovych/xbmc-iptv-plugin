# -*- coding: utf-8 -*-
__author__ = 'george'

import os
import pickle
import time
import urllib2
import difflib

class Channel(object):
    def __init__(self, name, image_url, info_url):
        self.name = name
        self.image_url = image_url
        self.info_url = info_url

    def __unicode__(self):
        return u'Channel : { Name: ' + unicode(self.name) +\
               u', Image: ' + (unicode(self.image_url) if self.image_url else u'None') +\
               u', Info: ' + (unicode(self.info_url) if self.info_url else u'None') + u' }'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return other.image_url == self.image_url and other.info_url == self.info_url


class ChannelDataCache(object):

    def getChannelsFromWeb(self):
        url = urllib2.urlopen(self.channel_update_url)
        try:
            time, channels = pickle.load(url)
        except:
            channels = None
        url.close()
        return channels

    def setChannels(self, channels, save=True):
        if channels is not None:
            self.channels = channels
        if save:
            f = open(self.channel_cache_file, 'wt')
            pickle.dump([time.time(), channels], f)
            f.close()

    def __init__(self, path, update_url, cache_time=300000, filename='channels.ch'):
        self.channel_cache_path = path
        self.channel_cache_file = os.path.join(path, filename)
        self.channel_update_url = update_url
        try:
            f = open(self.channel_cache_file, 'rt')
            update_time, channels = pickle.load(f)
            f.close()
            self.setChannels(channels, False)
            if time.time() - update_time > cache_time:
                self.setChannels(self.getChannelsFromWeb())
        except IOError:
            self.setChannels(set(), False)
            self.setChannels(self.getChannelsFromWeb())


class ChannelAdvancedSearch(object):
    #__search_dictionary__ = "__search_dictionary__"
    #__channel_objects__ = "__channel_objects__"
    #__channel_count__ = "__channel_count__"

    def __replace_word_b_c_e(self, string, word):
        if string[:len(word)+1] == word + ' ':
            string = string[len(word)+1:]
        return self.__replace_word_c_e(string, word)

    def __replace_word_c_e(self, string, word):
        if string[-len(word)-1:] == ' ' + word:
            string = string[:-len(word)-1]
        return string.replace(' ' + word + ' ', ' ')

    def cleanString(self, string, country_string = None):
        string = string.strip().lower()
        string = string.replace('(', '').replace(')', '')
        string = string.replace('_', ' ').replace('-', ' ').replace(u'плюс','+')
        string = string.replace('+', ' + ').replace(u'x', u' x ').replace('*', ' ').replace(u'х', u' x ').strip()
        string = self.__replace_word_b_c_e(self.__replace_word_b_c_e(string, u'канал'), u'channel')
        string = self.__replace_word_b_c_e(self.__replace_word_b_c_e(self.__replace_word_b_c_e(string, u'трк'), u'тк'), u'тв')
        string = self.__replace_word_b_c_e(self.__replace_word_b_c_e(string, u'hd'), u'tv')
        string = string.replace('.', ' ').replace('!', ' ').replace(u'tv', u' tv ').replace(u'тв', u' тв ').strip()
        if country_string is not None:
            string = self.__replace_word_c_e(string, country_string)
            string = string + " " + country_string.capitalize()
        return string.replace('  ', ' ').replace('  ', ' ')

    def addNewChannel(self, channel, channel_list):
        channel_list.add(channel)

    def getChannel(self, name, channel_set, country_string=None):
        channel_names = [channel.name for channel in channel_set]
        name = self.cleanString(name, country_string)
        found = difflib.get_close_matches(name, channel_names, 10, 0.3)
        if len(found) > 0:
            for channel in channel_set:
                if channel.name == found[0]:
                    return channel
        return None

