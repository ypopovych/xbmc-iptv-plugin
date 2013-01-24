#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'george'

import sys, xbmc, xbmcaddon, xbmcgui, xbmcplugin, os
from urlparse import urlparse
from cache import FileCache
from channel_info_provider import InfoProvider


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class M3UCache(FileCache):
    def getURL(self, key):
        return key

    def getFileItemName(self, key):
        urlparts = urlparse(key)
        name = urlparts[1]
        if name == "":
            name = os.path.basename(urlparts[2])
        return name + '.m3u'

class Plugin(object):

    MODE = enum('OPEN_PLAYLIST', 'PLAY_VIDEO')

    __channels_folder_url__ = 'http://github.com/IICUX/xbmc-iptv-plugin/raw/master/support/iptv.viewer/db'
    __channels_file_names__ = ( 'ruchannels.ch', 'uachannels.ch' )
    __channel_country_strings__ = ( u'россия', u'украина')

    def __init__(self, script, handle, settings, params = None):
        self.script = script
        self.handle = handle
        self.settings = settings
        self.path = settings.getAddonInfo('path')
        self.m3u_cache = None
        self.info_provider = None
        self.channel_updates = self.__channels_folder_url__ + '/' + self.__channels_file_names__[int(settings.getSetting('channel_list'))]
        self.channel_country = self.__channel_country_strings__[int(settings.getSetting('channel_list'))]

        playlists = settings.getSetting('playlists') + ',' + settings.getSetting('playlists2') + ',' +\
                    settings.getSetting('playlists3') + ',' + xbmc.translatePath('special://profile/playlists/iptv')
        self.playlists = self.getPlaylistList(playlists)

        if params is not None:
            self.params = self.getParams(params)
        else:
            self.params = {}

    def __getM3UCache(self):
        if self.m3u_cache is None:
            self.m3u_cache = M3UCache(os.path.join(os.path.join(os.path.join(self.path,'resources'), 'media'), 'm3u_cache'))
        return self.m3u_cache

    def __getInfoProvider(self):
        if self.info_provider is None:
            self.info_provider = InfoProvider(os.path.join(os.path.join(self.path,'resources'), 'media'), self.channel_updates, self.channel_country)
        return self.info_provider

    def getPlaylistList(self, playlists):
        playlists = playlists.split(',')
        playlist_files = []
        for playlist in playlists:
            if playlist != '':
                url = urlparse(playlist)
                if url.scheme == "http":
                    playlist_files.append(self.__getM3UCache().getFilePath(playlist))
                else:
                    if os.path.isdir(playlist):
                        for file in os.listdir(playlist):
                            if file.rfind(".m3u") != -1:
                                playlist_files.append(os.path.join(playlist, file))
                    else:
                        if playlist.rfind(".m3u") != -1:
                            playlist_files.append(playlist)
        return playlist_files

    def getParams(self, params):
        params_dict = {}
        pairs = params.split('?')[1].split('&')
        for pair in pairs:
            data = pair.split('=')
            params_dict[data[0]] = data[1]
        return params_dict
        
    def readPlaylist(self, playlist):
        image = os.path.join(self.path, 'icon.png')
        files = []

        file = open(playlist, "rt")
        file.readline()
        name = "bad_m3u"
        for line in file:
            if line[0] == '#':
                if line[:5] == '#EXTI':
                    name = line[line.find(',')+1:]
                    name = unicode(name, 'utf8', 'ignore').strip()
            else:
                try:
                    icon = self.__getInfoProvider().getImageURL(name)
                except KeyError:
                    icon = image
                if icon is None:
                    icon = image
                files.append( (name, line, icon) )
        file.close()
        return files

    def showChannels(self):
        playlist = self.playlists[int(self.params["playlist"])]

        files = self.readPlaylist(playlist)
        index = 0
        for name, url, icon in files:
            listitem = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            purl = self.script + "?mode=" + str(self.MODE.PLAY_VIDEO) + "&playlist=" + self.params["playlist"] + '&video=' + str(index)
            xbmcplugin.addDirectoryItem(self.handle, purl, listitem, False)
            index+=1
        xbmcplugin.endOfDirectory(self.handle)
	
    def playVideo(self):
        playlist = self.playlists[int(self.params['playlist'])]
        video = int(self.params['video'])

        resultPlaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        resultPlaylist.clear()
        
        files = self.readPlaylist(playlist)
        for name, url, icon in files:
            listitem = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            resultPlaylist.add(url, listitem)
        player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        player.play(resultPlaylist)
        player.playselected(video)
		
	
    def execute(self):
        self.MODE_FUNC[int(self.params['mode'])](self)

    def printPlaylists(self):
        if len(self.playlists) > 1:
            index = 0
            for playlist in self.playlists:
                name = os.path.basename(playlist)
                name = name[:name.rfind('.')]
                item = xbmcgui.ListItem(name)
                item.setInfo(type = "Video", infoLabels = {"Title": name} )
                purl = self.script + "?mode=" + str(self.MODE.OPEN_PLAYLIST) + "&playlist=" + str(index)
                index += 1
                xbmcplugin.addDirectoryItem(self.handle, purl, item, True)
            xbmcplugin.endOfDirectory(self.handle)
        else:
            self.params["mode"] = self.MODE.OPEN_PLAYLIST
            self.params["playlist"] = '0'
            self.execute()

    MODE_FUNC = { MODE.OPEN_PLAYLIST: showChannels, MODE.PLAY_VIDEO: playVideo}


if __name__ == "__main__":
    settings = xbmcaddon.Addon(id="plugin.video.iptv.viewer")
    if not sys.argv[2]:
        Plugin(sys.argv[0], int(sys.argv[1]), settings).printPlaylists()
    else:
        Plugin(sys.argv[0], int(sys.argv[1]), settings, sys.argv[2]).execute()
