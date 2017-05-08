# -*- coding: utf-8 -*-
# Module: default
import sys
import json, copy
import requests
import re
import urllib
from urllib import urlencode
from urlparse import parse_qsl
from BeautifulSoup import BeautifulSoup
import xbmc
import xbmcgui
import xbmcplugin
# from dialogs.DialogMovieInfo import DialogMovieInfo

# Get the plugin url in plugin:// notation.
# _url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Get Url
CHANNEL_ID = 'UCF1JIbMUs6uqoZEY1Haw0GQ'
API_KEY = 'AIzaSyAiC_r7jE_iQEKGYkVZMk5I-BXnz3v4cz0'
BASE_URL = "https://www.googleapis.com/youtube/v3/"
DefaultPageToken = 'CAUQAQ'


def main_list(name, thumb, mode, id, nextPageToken, isFolder=False, video_id=None):
    xbmc.log('IN FUN=main_list()......', 2)
    # xbmc.log('name : ' + str(name), 2)
    u = "plugin://plugin.video.example/"
    u += "?name=" + urllib.quote_plus(str(name))
    u += "&thumb=" + urllib.quote_plus(str(thumb))
    u += "&action=" + str(mode)
    u += "&video_id=" + str(video_id)
    u += "&playlist_id=" + str(id)
    u += "&nextPageToken="+ str(nextPageToken)
    xbmc.log('url ..........................: ' + str(u), 2)
    liz = xbmcgui.ListItem(label=urllib.unquote_plus(name), iconImage="", thumbnailImage=urllib.unquote_plus(thumb))
    liz.setInfo(type="video", infoLabels={"label": name, "title": name})
    liz.addContextMenuItems([('Refresh', 'Container.Refresh')])
    liz.setArt({'poster': thumb})
    # xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url=u, listitem=liz, isFolder=True)
    xbmcplugin.addDirectoryItem(abs(int(sys.argv[1])), u, liz, isFolder)


def load_playlist(page_token=None):
    # load playlists from channel
    xbmc.log('In FUN=load_playlist()  **********', 2)
    if page_token == None:
        page_token = 'CAUQAQ'
    else:
        pass
    load_channel_list = requests.get(BASE_URL+"playlists?part=snippet&maxResults=25&channelId=" + str(CHANNEL_ID) + "&key=" + str(API_KEY) + "&pageToken="+str(page_token))
    playlist_details = json.loads(load_channel_list.text)
    # xbmc.log('RESPONSE : ' + str(playlist_details), 2)
    for item in playlist_details['items']:
        title = urllib.quote_plus(item['snippet']['title'])
        xbmc.log("title---------"+str(title), 2)
        standard_thumb = urllib.quote_plus(item['snippet']['thumbnails']['default']['url'])
        xbmc.log("thumb---------"+str(standard_thumb), 2)
        main_list(str(title), standard_thumb, 'playlist_list', item['id'], playlist_details['nextPageToken'], isFolder=True, video_id=None)
    xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url='{0}?action=next_page&nextPageToken={1}'.format('plugin://plugin.video.example/', playlist_details['nextPageToken']), listitem=xbmcgui.ListItem(label='Next Page >>>'), isFolder=True)


def list_videos(playlist_id, page_token=''):
    next_video_page_token = ''
    xbmc.log('In FUN=load_videos()  ############**********', 2)
    load_playlist_list = requests.get(BASE_URL + "playlistItems?part=snippet&maxResults=2&key=AIzaSyAiC_r7jE_iQEKGYkVZMk5I-BXnz3v4cz0&playlistId=" + str(playlist_id) + "&pageToken="+str(page_token))
    video_list = json.loads(load_playlist_list.text)
    xbmc.log('RESPONSE : ' + str(video_list), 2)
    if video_list['pageInfo']['totalResults'] > video_list['pageInfo']['resultsPerPage']:
        next_video_page_token = video_list['nextPageToken']
    for item in video_list['items']:
        title = urllib.quote_plus(item['snippet']['title'])
        xbmc.log("title---------" + str(title), 2)
        standard_thumb = urllib.quote_plus(item['snippet']['thumbnails']['default']['url'])
        xbmc.log("thumb---------" + str(standard_thumb), 2)
        main_list(str(title), standard_thumb, 'play', item['id'], next_video_page_token, isFolder=True, video_id=None)
    xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url='{0}?action=next_video_page&nextPageToken={1}'.format('plugin://plugin.video.example/', next_video_page_token), listitem=xbmcgui.ListItem(label='Next Page >>>'), isFolder=True)    


def router():
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    xbmc.log('ALL_PARAMS : ' + str(param), 2)
    if param:
        if param['action'] == 'next_page':
            # xbmc.log("----------------------here" + str(param['movies']), 2)
            xbmc.log('Param : next_page', 2)
            load_playlist(param['nextPageToken'])
        if param['action'] == 'next_video_page':
            # xbmc.log("----------------------here" + str(param['movies']), 2)
            xbmc.log('Param : next_video_page', 2)
            list_videos(param['nextPageToken'])
        elif param['action'] == 'playlist_list':
            xbmc.log('Param : playlist_list', 2)
            list_videos(param['playlist_id'])
        #     xbmc.log('Param : listing details successful ', 2)
        # elif param['action'] == 'load':
        #     xbmc.log('Param : loading page ', 2)
        #     list_videos(param['page_num'])
        #     xbmc.log('Param : loading page successful!', 2)
        else:
            xbmc.log('Param : value error', 2)
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        xbmc.log('Param : listing playlists', 2)
        load_playlist()
        xbmc.log('Param : All playlists of current page is loaded', 2)


if __name__ == '__main__':
    # router(sys.argv[2][1:])
    xbmc.log('start.....................', 2)
    # xbmc.executebuiltin('LoadProfile(master user)')
    router()
    xbmcplugin.endOfDirectory(_handle,  cacheToDisc=False)