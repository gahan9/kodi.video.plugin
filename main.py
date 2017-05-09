# -*- coding: utf-8 -*-

import sys
import json
import requests
import re
import urllib
import xbmc
import xbmcgui
import xbmcplugin

# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# list of acceptance youtube channel url type
URL_ACCEPT_EXAMPLES = ['https://www.youtube.com/user/MARVEL/', 
                        'https://www.youtube.com/playlist?list=PLVfin74Qx3tV8bgAhzbfDpnfPoGmJWAcn',
                        'https://www.youtube.com/channel/UCqwUrj10mAEsqezcItqvwEw/playlists',
                        'https://www.youtube.com/watch?v=Kv1ZCdDKdKw&index=2&list=PLK5HARgNfgj-qJdlFsVrlLmRIr3wmcIce',
                        'https://www.youtube.com/watch?v=Kv1ZCdDKdKw']
# url of youtube channel
URL = 'https://www.youtube.com/watch?v=VSB4wGIdDwo&index=2&list=PLVfin74Qx3tV8bgAhzbfDpnfPoGmJWAcn'
# youtube api key
API_KEY = 'AIzaSyAiC_r7jE_iQEKGYkVZMk5I-BXnz3v4cz0'
# base url for all youtube api request
BASE_URL = "https://www.googleapis.com/youtube/v3/"
# global variable for channel id
CHANNEL_ID = ''

MAX_PLAYLIST_PER_PAGE = 15
MAX_VIDEOS_PER_PAGE = 15


def get_channel_id(url):
    """
    Get channel id of youtube channel from URL
    :param url: youtube channel URL
    :return: channel id
    """
    # xbmc.log('IN FUN=get_channel_id()......', 2)  # log : NOTICE
    channel_url_split = url.split('/')
    if 'user' in channel_url_split:
        # URL type : https://www.youtube.com/user/MARVEL/playlists
        index_user = channel_url_split.index('user') + 1
        channel_name = channel_url_split[index_user]
        # xbmc.log('channel_name ===========' + str(channel_name), 2)  # log : NOTICE
        load_channel_id = requests.get(BASE_URL + "channels?part=snippet&key=" + str(API_KEY) + "&forUsername=" + str(channel_name))
        channel_content = json.loads(load_channel_id.text)
        id_channel = channel_content['items'][0]['id']
        return id_channel
    elif 'channel' in channel_url_split:
        # URL type : https://www.youtube.com/channel/UCqwUrj10mAEsqezcItqvwEw/playlists
        index_channel = channel_url_split.index('channel') + 1
        channel_id = channel_url_split[index_channel]
        return channel_id


def main_list(name, thumb, mode, id, nextPageToken, isFolder=False, video_id=None, total_videos=None):
    """
    Create Directory item in Kodi
    :param name: label name
    :param thumb: thumb art
    :param mode: specified action
    :param id: youtube playlist id
    :param nextPageToken: token to next page
    :param isFolder: True if contains list within else False
    :param video_id: youtube video id
    :param total_videos: total number of videos within current playlist
    :return: create single list item in Kodi
    """
    xbmc.log('IN FUN=main_list()......', 2)  # log : NOTICE
    xbmc.log('name : ' + str(name), 2)  # log : NOTICE
    u = "plugin://plugin.video.example/"
    u += "?name=" + urllib.quote_plus(str(name))
    u += "&thumb=" + urllib.quote_plus(str(thumb))
    u += "&action=" + str(mode)
    u += "&video_id=" + str(video_id)
    u += "&playlist_id=" + str(id)
    u += "&nextPageToken=" + str(nextPageToken)
    xbmc.log('url ..........................: ' + urllib.unquote_plus(str(u)), 2)  # log : NOTICE
    if video_id == None:
        cust_label = urllib.unquote_plus(name) + '[B][COLOR red] (' + str(total_videos) + ") [/COLOR][/B]"
    else:
        cust_label = urllib.unquote_plus(name)
    liz = xbmcgui.ListItem(label=cust_label, iconImage="", thumbnailImage=urllib.unquote_plus(thumb))
    liz.setInfo(type="video", infoLabels={"label": name, "title": name})
    liz.addContextMenuItems([('Refresh', 'Container.Refresh')])
    liz.setArt({'poster': thumb})
    # xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url=u, listitem=liz, isFolder=True)
    xbmcplugin.addDirectoryItem(abs(int(sys.argv[1])), u, liz, isFolder)


def load_playlist(page_token):
    """
    Load all playlists from given channel url
    :param page_token: token to redirect to next page
    :return: display list of playlist from channel in Kodi
    """
    # xbmc.log('In FUN=load_playlist()  **********', 2)  # log : NOTICE
    channel_id = get_channel_id(URL)
    load_channel_list = requests.get(BASE_URL + "playlists?part=contentDetails%2Csnippet&maxResults=" + str(MAX_PLAYLIST_PER_PAGE) + "&channelId=" + str(channel_id) + "&key=" + str(API_KEY) + "&pageToken="+str(page_token))
    playlist_details = json.loads(load_channel_list.text)
    # xbmc.log('RESPONSE : ' + str(playlist_details), 2)  # log : NOTICE
    for item in playlist_details['items']:
        # replace non-alphanumeric characters of title using regex
        title = re.sub("[^a-zA-Z0-9#!]+", " ", item['snippet']['title'])
        # title = urllib.quote_plus(item['snippet']['title'])
        xbmc.log("title---------"+str(title), 2)
        if 'thumbnails' in item['snippet'].keys():
            standard_thumb = urllib.quote_plus(item['snippet']['thumbnails']['default']['url'])
        else:
            standard_thumb = 'http://lookpic.com/O/i2/1246/NNl4XqJG.jpeg'
        # xbmc.log("thumb---------"+str(standard_thumb), 2)
        total_vids = item['contentDetails']['itemCount']
        if 'nextPageToken' in playlist_details.keys():
            token = playlist_details['nextPageToken']
        else:
            token = ''
        main_list(str(title), standard_thumb, 'playlist_list', item['id'], token, isFolder=True, video_id=None, total_videos=total_vids)
    if 'nextPageToken' in playlist_details.keys():
        xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url='{0}?action=next_playlis_page&nextPageToken={1}'.format('plugin://plugin.video.example/', playlist_details['nextPageToken']), listitem=xbmcgui.ListItem(label='Next Page >>>'), isFolder=True)


def list_videos(playlist_id, page_token=''):
    """
    load videos from playlist
    :param playlist_id: playlist
    :param page_token: page token to load next page (if given)
                        '' for default page
    :return: display list of videos from playlist in Kodi
    """
    next_video_page_token = ''
    # xbmc.log('In FUN=load_videos()  ############**********', 2)  # log : NOTICE
    load_playlist_list = requests.get(BASE_URL + "playlistItems?part=snippet&maxResults=" + str(MAX_VIDEOS_PER_PAGE) + "&key=" + str(API_KEY) + "&playlistId=" + str(playlist_id) + "&pageToken="+str(page_token))
    video_list = json.loads(load_playlist_list.text)
    # xbmc.log('RESPONSE : ' + str(video_list), 2)  # log : NOTICE
    if 'nextPageToken' in video_list.keys():
        next_video_page_token = video_list['nextPageToken']
    for item in video_list['items']:
        # replace non-alphanumeric characters of title using regex
        title = re.sub("[^a-zA-Z0-9#!]+", " ", item['snippet']['title'])
        # xbmc.log("title---------" + str(title), 2)  # log : NOTICE
        if 'thumbnails' in item['snippet'].keys():
            standard_thumb = urllib.quote_plus(item['snippet']['thumbnails']['default']['url'])
        else:
            standard_thumb = 'http://lookpic.com/O/i2/1246/NNl4XqJG.jpeg'
        if title == "Private video":
            continue  
        video_id = item['snippet']['resourceId']['videoId']
        # xbmc.log("thumb---------" + str(standard_thumb), 2)
        main_list(str(title), standard_thumb, 'play', item['snippet']['playlistId'], next_video_page_token, isFolder=False, video_id=video_id)
    if 'nextPageToken' in video_list.keys():
        xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url='{0}?action=next_video_page&nextPageToken={1}&playlistId={2}'.format('plugin://plugin.video.example/', next_video_page_token, playlist_id), listitem=xbmcgui.ListItem(label='Next Page >>>'), isFolder=True)


def get_single_video(videoId):
    """
    Create list item for single video
    :param videoId: youtube video id
    :return: creates list item for video in Kodi
    """
    # xbmc.log('In FUN=get_single_video()  ############**********', 2)  # log : NOTICE
    load_video_info = requests.get(BASE_URL + "videos?part=snippet""&key=" + str(API_KEY) + "&id=" + str(videoId))
    video_info = json.loads(load_video_info.text)
    title = re.sub("[^a-zA-Z0-9#!]+", " ", video_info['items'][0]['snippet']['title'])
    # xbmc.log('Title : ' + str(title), 2)  # log : NOTICE
    url = '{0}?action=play&video_id={1}'.format('plugin://plugin.video.example/', videoId)
    listitem=xbmcgui.ListItem(label=title)
    xbmcplugin.addDirectoryItem(abs(int(sys.argv[1])), url, listitem, isFolder=False)
    xbmcplugin.endOfDirectory(_handle)


def router(url):
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
        try:
            if param['action'] == 'next_playlis_page':
                # xbmc.log("----------------------here" + str(param['movies']), 2)  # log : NOTICE
                # xbmc.log('Param : next_playlis_page', 2)  # log : NOTICE
                load_playlist(param['nextPageToken'])
                # xbmc.log('Param : Requested page successfully loaded', 2)  # log : NOTICE
            if param['action'] == 'next_video_page':
                # xbmc.log("----------------------here" + str(param['movies']), 2)  # log : NOTICE
                # xbmc.log('Param : next_video_page', 2)  # log : NOTICE
                list_videos(param['playlistId'], param['nextPageToken'])
            elif param['action'] == 'playlist_list':
                # xbmc.log('Param : playlist_list', 2)  # log : NOTICE
                list_videos(param['playlist_id'])
                # xbmc.log('Param : videos details successful ', 2)  # log : NOTICE
            elif param['action'] == 'play':
                xbmc.log('------PLAY--------------' + str(param['video_id']) + str(type(param['video_id'])), 2)  # log : NOTICE
                xbmc.Player().play("plugin://plugin.video.youtube/play/?action=play_video&video_id=%s" % param['video_id'])
        except Exception as e:
            # xbmc.log(str(e), 2)  # log : NOTICE
            # xbmc.log('exception in param........' + str(paramstring), 2)  # log : NOTICE
            raise ValueError('Ooopps!! Invalid parameter : ' + str(paramstring))
    else:
        try:
            if '?' in url:
                channel_url_split = url.split('?')[1]
                xbmc.log('------ITEM---' + str(channel_url_split), 2)
                if 'v=' in channel_url_split:
                    if '&' in channel_url_split:
                        # URL type : https://www.youtube.com/watch?v=Kv1ZCdDKdKw&index=2&list=PLK5HARgNfgj-qJdlFsVrlLmRIr3wmcIce
                        item_split = channel_url_split.split('&')
                        xbmc.log('------ITEM-SPLIT---' + str(item_split), 2)
                        for v_id in item_split:
                            if 'v=' in v_id:
                                vid = v_id.replace('v=', '')
                                get_single_video(vid)
                    else:
                        # URL type : https://www.youtube.com/watch?v=Kv1ZCdDKdKw
                        vid = channel_url_split.replace('v=', '')
                        xbmc.log('.............' + str(vid), 2)
                        get_single_video(vid)
                elif 'list=' in channel_url_split:
                    # URL type : https://www.youtube.com/playlist?list=PLK5HARgNfgj-qJdlFsVrlLmRIr3wmcIce
                    playlist_id = channel_url_split.replace('list=', '')
                    list_videos(playlist_id)
            else:
                xbmc.log('Param : listing playlists', 2)  # log : NOTICE
                load_playlist('')
                xbmc.log('Param : All playlists of current page is loaded', 2)  # log : NOTICE
        except:
            # xbmcgui.Dialog().ok('Plugin Error!!!', 'Invalid URL entered!!! Example of acceptable urls are:', URL_ACCEPT_EXAMPLES[0], URL_ACCEPT_EXAMPLES[1], URL_ACCEPT_EXAMPLES[2], URL_ACCEPT_EXAMPLES[3], URL_ACCEPT_EXAMPLES[4])
            raise ValueError('Ooopps!! Invalid URL : ' + str(url))


if __name__ == '__main__':
    xbmc.log('Service Call.....................', 2)  # log : NOTICE
    router(URL)
    xbmcplugin.endOfDirectory(_handle,  cacheToDisc=False)
