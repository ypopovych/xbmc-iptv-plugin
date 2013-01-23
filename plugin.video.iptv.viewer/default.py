#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, xbmc, xbmcaddon, xbmcgui, xbmcplugin, os
from urlparse import urlparse
import urllib2
import pickle
import time
import shutil

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class URLCache(object):
    def __init__(self, path):
        self.cache_path = path
        self.cache_file = os.path.join(path, 'cache.dat')
        try:
            file = open(self.cache_file, "rt")
            self.urls = pickle.load(file)
            file.close()
        except IOError:
            self.urls = {}
            shutil.rmtree(self.cache_path)
            os.mkdir(self.cache_path)
        self.clear_deleted()

    def clear_deleted(self):
        files = []
        for val in self.urls.values():
            files.append(os.path.basename(val[0]))

        cache = os.listdir(self.cache_path)
        for f in cache:
            if f not in files:
                os.remove(os.path.join(self.cache_path, f))

    def save(self):
        fd = open(self.cache_file, 'wt')
        pickle.dump(self.urls, fd)
        fd.close()

    def updateCache(self, url):
        try:
            file, aTime = self.urls[url]
            os.remove(file)
        except KeyError:
            pass
        fd = urllib2.urlopen(url)
        name = urlparse(url)[1]
        if name == "":
            name = "unnamed_url"
        file = os.path.join(self.cache_path, name) + '.m3u'
        fd2 = open(file, 'wb')
        fd2.write(fd.read())
        fd.close()
        fd2.close()

        self.save()
        self.urls[url] = (file, time.time())

    def getURL(self, url):
        try:
            file, aTime = self.urls[url]
        except KeyError:
            self.updateCache(url)
            file, aTime = self.urls[url]
        if (time.time() - aTime) > 32000:
            self.updateCache(url)
            file, aTime = self.urls[url]
        return file

class Plugin(object):

    MODE = enum('OPEN_PLAYLIST', 'PLAY_VIDEO')

    def __init__(self, script, handle, settings, params = None):
        self.script = script
        self.handle = handle
        self.settings = settings
        self.path = settings.getAddonInfo('path')
        self.url_cache = URLCache(os.path.join(os.path.join(os.path.join(self.path,'resources'), 'media'), 'm3u_cache'))

        playlists = settings.getSetting('playlists') + ',' + xbmc.translatePath('special://profile/playlists/iptv')
        self.playlists = self.getPlaylistList(playlists)
        if params is not None:
            self.params = self.getParams(params)
	else:
	    self.params = {}
        self.url_cache.save()

    def getPlaylistList(self, playlists):
        playlists = playlists.split(',')
        playlist_files = []
        for playlist in playlists:
            url = urlparse(playlist)
            if url.scheme == "http":
                playlist_files.append(self.url_cache.getURL(playlist))
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
        for line in file.xreadlines():
            if line[0] == '#':
                if line[:5] == '#EXTI':
                    name = line[line.find(',')+1:]
                    name = unicode(name, 'utf8', 'ignore').strip()
            else:
                files.append( (name, line, image) )
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


if (__name__ == "__main__"):
    settings = xbmcaddon.Addon(id="plugin.video.iptv.viewer")
    if (not sys.argv[2]):
        Plugin(sys.argv[0], int(sys.argv[1]), settings).printPlaylists()
    else:
        Plugin(sys.argv[0], int(sys.argv[1]), settings, sys.argv[2]).execute()
