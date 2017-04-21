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
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_page_number = 0

# Get Url
BASE_URL = "http://yts.ag/api/v2/list_movies.json"
_URI = "http://yts.ag/api/v2/list_movies.json"

VIDEOS = {}


def fetch_data(_URI, _page_number):
    # xbmc.log('fetching json file..............', 2)
    url_to_fetch = _URI + '?page_number=' + str(_page_number)
    # xbmc.log('fetching url : ' + url_to_fetch, 2)
    get_url_response = requests.get(url_to_fetch)
    if get_url_response.status_code == 200:
        return json.loads(get_url_response.text)
    else:
        return None


def load_page():
    # xbmc.log('loading page..........', 2)

    if _URI == BASE_URL:
        this_page = _page_number
    else:
        this_page = _page_number + 1
    json_data = fetch_data(_URI, this_page)
    # xbmc.log('type of json_data: ' + str(type(json_data)), 2)
    if json_data is not None:
        VIDEOS['movies'] = json_data['data']['movies']
        # xbmc.log('listing length: ' + str(VIDEOS.keys()), 2)


def json_update():
    xbmc.log('In json Update********', 2)
    xbmc.sleep(15)
    load_page()
    list_videos('movies')


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    # xbmc.log('formating url.......', 2)
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: list
    """
    # xbmc.log('Retriving categories', 2)
    return VIDEOS.iterkeys()


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    # xbmc.log('Retriving movie list.............', 2)
    # xbmc.log('Category is .............' + category, 2)
    # xbmc.log('Retriving movie list.............', 2)
    # xbmc.log('type of videos' + str(len(VIDEOS)), 2)
    return VIDEOS[category]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    xbmc.log('listing categories................', 2)

    load_page()
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category, iconImage=VIDEOS[category][0]['small_cover_image'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['medium_cover_image'],
                          'icon': VIDEOS[category][0]['small_cover_image'],
                          'fanart': VIDEOS[category][0]['background_image_original']})
        # Set additional info for the list item.
        # setInfo allows to set various information for an item.
        list_item.setInfo('video', {'name': VIDEOS[category][0]['title'],
                                    'genre': VIDEOS[category][0]['genres'][0],
                                    'rating': VIDEOS[category][0]['rating'],
                                    'release_year': VIDEOS[category][0]['year'],
                                    'details': VIDEOS[category][0]['description_full']})
        list_item.addContextMenuItems([('Refresh', 'Container.Refresh'),
                                       ('Go up', 'Action(ParentDir)')])
        list_item.setProperty('fanart_image', VIDEOS[category][0]['background_image_original'])
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # url = '{0}?action=listing&category={1}'.format(_url, category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Get the list of videos in the category.
    xbmc.log('in listing videos*******************************', 2)
    load_page()
    videos = get_videos(category)
    xbmc.log('video : ' + str(type(videos)), 2)
    # Iterate through videos.
    # panel = self.getControl(123)
    for video in videos:
        xbmc.log('single video object : ' + str(video), 2)
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['title'])
        list_item.setArt({'thumb': video['medium_cover_image'], 'icon': video['small_cover_image'], 'fanart': video['background_image']})
        # Set 'IsPlayable' property to 'true'. This is mandatory for playable items!
        # list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('fanart_image', video['background_image'])
        # listing.append((url, list_item, is_folder))
        list_item.addContextMenuItems([('Refresh', 'Container.Refresh'),
                                       ('Details', 'ActivateWindow(movieinformation)'),
                                       ('Next Page', 'ActivateWindow(100025)'),
                                       ('Go up', 'Action(ParentDir)')])
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        # url = get_url(action='play', video=video['video'])
        url = get_url(action='show', video=video['url'])
        # url = '{0}?action=listing&video={1}'.format(_url, video['url'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        # xbmcplugin.addDirectoryItem(_handle, url, listing, len(listing))
    # panel.addItems(listing)
    # next_page = xbmcgui.ListItem(label='more...')
    # xbmcplugin.addDirectoryItem(_handle, next_page, 'Container.Refresh')
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_details(movie_url):
    movie_details = []
    movie_page_request = requests.get(movie_url)
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
    # # return xbmc.executebuiltin('ActivateWindow(movieinformation)')
    # return xbmcgui.Dialog().ok(movie_name, movie_year, movie_genre, movie_rating)
    for info in movie_details:
        list_item = xbmcgui.ListItem(label=info)
        is_folder = False
        url = get_url(action='link', video=movie_url)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        list_item.setArt({'thumb': movie_thumb, 'icon': movie_thumb, 'fanart': movie_thumb})
        list_item.setInfo('video', {'title': movie_name, 'genre': movie_genre, 'rating': movie_rating})
    xbmcplugin.endOfDirectory(_handle)


def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            xbmc.log('Param : listing videos', 2)
            list_videos(params['category'])
            xbmc.log('Param : listing videos successful', 2)
        elif params['action'] == 'show':
            # Play a video from a provided URL.
            xbmc.log('Param : listing details', 2)
            list_details(params['video'])
            xbmc.log('Param : listing details successful ', 2)
            # xbmc.executebuiltin('ActivateWindow(movieinformation)')
        elif params['action'] == 'load':
            xbmc.log('Param : loading page ', 2)
            load_page()
            xbmc.log('Param : loading page successful!', 2)
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            xbmc.log('Param : value error', 2)
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        xbmc.log('Param : listing categories', 2)
        list_categories()
        xbmc.log('Param : listing categories successful', 2)



if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
    # list_categories()
