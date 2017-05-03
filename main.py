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
BASE_URL = "http://yts.ag/api/v2/list_movies.json?page=1"
_URI = ""

VIDEOS = {}
THIS_PAGE = {}


def fetch_data(page):
    xbmc.log('In FUN=fetch_data()  **********', 2)
    # xbmc.log('fetching json file..............', 2)
    _URI = BASE_URL.split("=")[0] + "=" + str(page)
    xbmc.log('page_yield() : ' + str(page), 2)
    xbmc.log('fetching url : ' + _URI, 2)
    get_url_response = requests.get(_URI)
    if get_url_response.status_code == 200:
        return json.loads(get_url_response.text)
    else:
        return None


def load_page(page_num):
    xbmc.log('In FUN=load_page() **********', 2)
    xbmc.log('URI : ' + _URI, 2)
    json_data = fetch_data(page_num)
    xbmc.log('type of json_data: ' + str(type(json_data)), 2)
    if json_data is not None:
        THIS_PAGE['page'] = json_data['data']['page_number']
        VIDEOS['movies'] = json_data['data']['movies']


def list_categories():
    xbmc.log('In FUN=list_categories()  **********', 2)
    load_page(1)
    categories = VIDEOS.iterkeys()
    xbmc.log('categories : ' + str(categories), 2)
    for category in categories:
        xbmc.log('************************** - - - - : - - ' + str(VIDEOS[category]), 2)
        main_list('Movies', urllib.quote_plus(VIDEOS[category][0]['medium_cover_image']), urllib.quote_plus(VIDEOS[category][0]['background_image_original']), 'listing', urllib.quote_plus(VIDEOS[category][0]['url']), isFolder=True)


def list_videos(page):
    xbmc.log('In FUN=list_videos()  **********', 2)
    # page += 1
    if page is None:
        cur_page = 1
    else:
        cur_page = int(page) + 1
    load_page(cur_page)
    movie_name = VIDEOS['movies']
    for video in movie_name:
        main_list(video['title_long'], urllib.quote_plus(str(video['medium_cover_image'])), urllib.quote_plus(str(video['background_image'])), 'show', urllib.quote_plus(str(video['url'])), isFolder=True)
    # xbmc.log("my data........" + str(VIDEOS['movies']), 2)
    # xbmc.log('videos : ' + str(videos), 2)

    xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url='{0}?action=load&page_num={1}'.format('plugin://plugin.video.example/', THIS_PAGE['page']), listitem=xbmcgui.ListItem(label='More >>>'), isFolder=True)


def main_list(name, thumb, fanart, mode, path, isFolder=False):
    # xbmc.log('IN FUN=main_list()......', 2)
    # xbmc.log('name : ' + str(path), 2)
    # xbmc.log('name : ' + str(urllib.unquote_plus(path)), 2)
    u = "plugin://plugin.video.example/"
    u += "?name=" + str(name)
    u += "&action=" + str(mode)
    u += "&url=" + str(urllib.unquote_plus(path))
    u += "&fanart=" + str(urllib.unquote_plus(fanart))
    u += "&thumb=" + str(urllib.unquote_plus(thumb))
    # xbmc.log('url' + str(u), 2)
    liz = xbmcgui.ListItem(label=name, iconImage="", thumbnailImage=thumb)
    liz.setInfo(type="video", infoLabels={"label": name, "title": name})
    liz.addContextMenuItems([('Refresh', 'Container.Refresh'),
                             ('Details', 'ActivateWindow(movieinformation)'),
                             ('Go up', 'Action(ParentDir)')])
    # metacache.insert("fanart", fanart)
    liz.setArt({'poster': thumb, 'fanart': fanart})
    xbmcplugin.addDirectoryItem(handle=abs(int(sys.argv[1])), url=u, listitem=liz, isFolder=True)


def list_details(movie_url):
    xbmc.log('In FUN=list_details()  **********', 2)
    movie_details = []
    movie_page_request = requests.get(urllib.unquote_plus(movie_url))
    movie_page_beutify = BeautifulSoup(movie_page_request.text)
    movie_info = movie_page_beutify.find('div', id='movie-info')
    movie_name = movie_info.findAll('h1')[0].string
    movie_thumb = movie_page_beutify.find('div', id='movie-poster').find('img').get('src')
    movie_year = 'Release Year: ' + movie_info.findAll('h2')[0].string
    movie_genre = 'Genre: ' + movie_info.findAll('h2')[1].string.replace('/', ',')
    movie_rating = 'Rating: ' + movie_info.findAll('span', itemprop="ratingValue")[0].string

    movie_details.append(movie_name)
    movie_details.append(movie_genre)
    movie_details.append(movie_rating)
    movie_details.append(movie_year)
    for info in movie_details:
        list_item = xbmcgui.ListItem(label=info)
        is_folder = False
        url = '{0}?action=donothing'.format('plugin://plugin.video.example/')
        list_item.setArt({'thumb': movie_thumb, 'icon': movie_thumb, 'fanart': movie_thumb})
        list_item.setInfo('video', {'title': movie_name, 'genre': movie_genre, 'rating': movie_rating})
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


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
        if param['action'] == 'listing':
            # xbmc.log("----------------------here" + str(param['movies']), 2)
            xbmc.log('Param : listing videos', 2)
            list_videos(0)
            xbmc.log('Param : listing videos successful', 2)
        elif param['action'] == 'show':
            xbmc.log('Param : listing details', 2)
            list_details(param['url'])
            xbmc.log('Param : listing details successful ', 2)
        elif param['action'] == 'load':
            xbmc.log('Param : loading page ', 2)
            list_videos(param['page_num'])
            xbmc.log('Param : loading page successful!', 2)
        else:
            xbmc.log('Param : value error', 2)
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        xbmc.log('Param : listing categories', 2)
        list_categories()
        xbmc.log('Param : listing categories successful', 2)


if __name__ == '__main__':
    # router(sys.argv[2][1:])
    xbmc.log('start.....................', 2)
    xbmc.executebuiltin('LoadProfile(profilename,[prompt])')
    router()
    xbmcplugin.endOfDirectory(_handle,  cacheToDisc=False)