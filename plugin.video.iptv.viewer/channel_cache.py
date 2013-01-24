# -*- coding: utf-8 -*-
__author__ = 'george'

import os
import pickle
import time
import urllib2

class Channel(object):
    def __init__(self, name, image_url, info_url):
        self.name = name
        self.image_url = image_url
        self.info_url = info_url
        self.id = 0

    def __unicode__(self):
        return u'Channel : { ID: ' + unicode(self.id) + u', Name: ' + unicode(self.name) +\
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

    def setChannels(self, channels, save = True):
        if channels is not None:
            self.channels = channels
        if save:
            f = open(self.channel_cache_file, 'wt')
            pickle.dump( [time.time(), channels], f)
            f.close()

    def __init__(self, path, update_url, cache_time = 300000, filename = 'channels.ch'):
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
            self.setChannels({}, False)
            self.setChannels(self.getChannelsFromWeb())

class ChannelAdvancedSearch(object):

    __search_dictionary__ = "__search_dictionary__"
    __channel_objects__ = "__channel_objects__"
    __channel_count__ = "__channel_count__"

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
        return string.replace('  ', ' ').replace('  ', ' ')

    def addNewChannel(self, channel, channel_list):
        parts = self.cleanString(channel.name).split(' ')

        count = channel_list.get(self.__channel_count__, 0)
        channel_list[self.__channel_count__] = count + 1
        channel.id = count

        repeats = {}
        for part in parts:
            if part != '':
                repeats[part] = repeats.get(part, 0) + 1

        print channel, repeats

        for key in repeats:
            repeat_key = key
            for i in range(1,repeats[key]):
                repeat_key = repeat_key + u'_' + key
            self.__add_channel(repeat_key,channel, channel_list)
            if key != repeat_key:
                self.__add_channel(key, channel, channel_list)
        self.__add_channel('('+str(len(parts))+')', channel, channel_list)

    def __add_channel(self, key, channel, channel_list):
        try:
            channel_objs = channel_list[self.__channel_objects__]
        except:
            channel_objs = {}
            channel_list[self.__channel_objects__] = channel_objs
        try:
            search_lists = channel_list[self.__search_dictionary__]
        except:
            search_lists = {}
            channel_list[self.__search_dictionary__] = search_lists
        channel_objs[channel.id] = channel
        try:
            search_lists[key].add(channel.id)
        except KeyError:
            st = set()
            st.add(channel.id)
            search_lists[key] = st

    def __find(self, sets):
        sets_length = len(sets)
        if sets_length > 1:
            new_sets = set()
            i = 0
            for left in sets:
                if i < sets_length-1:
                    j = 0
                    for right in sets:
                        if j > i:
                            the_set = left.intersection(right)
                            if len(the_set) > 0:
                                new_sets.add(the_set)
                        j += 1
                else:
                    break
                i += 1
            return self.__find(new_sets)

        try:
            for item in sets.pop():
                return item
        except KeyError:
            return None

    def getChannel(self, name, channel_list, country_string = None):
        parts = self.cleanString(name, country_string).split(' ')

        repeats = {}
        for part in parts:
            if part != '':
                repeats[part] = repeats.get(part, 0) + 1

        sets = set()
        for key in repeats:
            repeat_key = key
            for i in range(1,repeats[key]):
                repeat_key = repeat_key + u'_' + key
            if key != repeat_key:
                try:
                    channels = channel_list[self.__search_dictionary__][key]
                    sets.add(frozenset(channels))
                except:
                    pass
            try:
                channels = channel_list[self.__search_dictionary__][repeat_key]
                sets.add(frozenset(channels))
            except:
                pass
        try:
            channels = channel_list[self.__search_dictionary__]['('+str(len(parts))+')']
            sets.add(frozenset(channels))
        except:
            pass
        res = self.__find(sets)
        if res is not None:
            try:
                return channel_list[self.__channel_objects__][res]
            except:
                pass
        return None

