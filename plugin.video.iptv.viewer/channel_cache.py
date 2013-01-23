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

    def __str__(self):
        return "Channel : { ID: " + str(self.id) + ", Name: "+ self.name.encode('ascii', 'ignore') +", Image: " + self.image_url + ", Info: " + self.info_url + " }"

    def __eq__(self, other):
        return other.image_url == self.image_url and other.info_url == self.info_url



class ChannelUrlCache(object):
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

    def cleanString(self, string):
        string = string.strip().lower()
        string = string.replace('(', '').replace(')', '')
        string = string.replace('_', ' ').replace('.', ' ')
        string = string.replace(u'плюс','+').replace(u'минус','-')
        string = string.replace(u' трк', '').replace(u'трк ', '').replace(u' тк', '').replace(u'тк ', '')
        string = string.replace(u' hd', '').replace(u'hd ', '').replace(u' tv', '').replace(u'tv ', '')
        string = string.replace('+', ' + ').replace('-', ' - ').replace(u'x', u' x ').replace('*', ' ').replace(u'х', u' x ')
        return string

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
            str = key
            for i in range(1,repeats[key]):
                str = str + u'_' + key
            self.__add_channel(str,channel, channel_list)
            if key != str:
                self.__add_channel(key, channel, channel_list)

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
            new_sets = []
            for i in range(0, sets_length):
                for j in range(i+1, sets_length):
                    the_set = sets[i].intersection(sets[j])
                    if len(the_set) > 0:
                        new_sets.append(the_set)
            if len(new_sets) > 1:
                cur_len = len(new_sets[0])
                for the_set in new_sets:
                    if len(the_set) != cur_len:
                        return self.__find(new_sets)
        else:
            new_sets = sets
        if len(new_sets) > 0:
            for item in new_sets[0]:
                return item
        return None

    def getChannel(self, name, channel_list):
        parts = self.cleanString(name).split(' ')

        repeats = {}
        for part in parts:
            if part != '':
                repeats[part] = repeats.get(part, 0) + 1

        sets = []
        for key in repeats:
            str = key
            for i in range(1,repeats[key]):
                str = str + u'_' + key
            if key != str:
                try:
                    channels = channel_list[self.__search_dictionary__][key]
                    sets.append(channels)
                except:
                    pass
            try:
                channels = channel_list[self.__search_dictionary__][str]
                sets.append(channels)
            except:
                pass
        res = self.__find(sets)
        if res is not None:
            try:
                return channel_list[self.__channel_objects__][res]
            except:
                pass
        return None

