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

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Get Url
LIST_MOVIES_JSON = "http://yts.ag/api/v2/list_movies.json"
# base_url = "https://yts.ag/api/v2/list_movies.json"
# uri = ''
opt_qualities = ['720p', '1080p', '3D', 'ALL']
opt_ratings = range(10)
opt_sorts = ['date', 'seeds', 'size', 'alphabet', 'rating']
opt_orders = ['desc', 'asc']

movie_list_params = {
    'limit': 20,  # Maximum number of returned items
    'set': 1,  # Which set (page) do you want to return?
    'quality': 'ALL',  # {720p, 1080p, 3D, ALL}
    'rating': 0,  # Minimum rating between 0 - 9
    'keywords': '',  # {String}
    'genre': 'ALL',  # {String} Refer to http://www.imdb.com/genre/
    'sort': 'date',  # {date, seeds, size, alphabet, rating}
    'order': 'desc'  # {desc, asc}
}

VIDEOS = {}


def fetch_data(url):
    """
    Fetch Json file and return as python list if response is 200
x[]
    :param url: json url
    :return: list if success else None
    """
    get_url_response = requests.get(url)
    if get_url_response.status_code == 200:
        return json.loads(get_url_response.text)
    else:
        return None


xbmc.log("got url")
json_data = fetch_data(LIST_MOVIES_JSON)
if json_data is not None:
    VIDEOS['movies'] = json_data['data']['movies']
xbmc.log("got data")


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
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
    return VIDEOS[category]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['medium_cover_image'],
                          'icon': VIDEOS[category][0]['small_cover_image'],
                          'fanart': VIDEOS[category][0]['background_image_original']})
        # Set additional info for the list item.
        # setInfo allows to set various information for an item.
        list_item.setInfo('video', {'title': VIDEOS[category][0]['title_long'],
                                    'genre': VIDEOS[category][0]['genres'][0],
                                    'rating': VIDEOS[category][0]['rating'],
                                    'release_year': VIDEOS[category][0]['year'],
                                    'details': VIDEOS[category][0]['description_full']})
        list_item.addContextMenuItems([('Refresh', 'Container.Refresh'),
                                       ('Go up', 'Action(ParentDir)')])
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['title'], 'genre': video['genres'][0]})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['medium_cover_image'], 'icon': video['small_cover_image'], 'fanart': video['background_image_original']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        # list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('fanart', video['background_image_original'])
        list_item.addContextMenuItems([('Refresh', 'Container.Refresh'),
                                       ('Details', 'ActivateWindow(songinformation)'),
                                       ('Go up', 'Action(ParentDir)')])
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        # url = get_url(action='play', video=video['video'])
        url = get_url(action='show', video=video['url'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        # xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_details(arg):
    """

    :param arg:
    :return:
    """
    movie_page_request = requests.get(arg)
    movie_page_beutify = BeautifulSoup(movie_page_request.text)
    movie_info = movie_page_beutify.find('div', id='movie-info')
    movie_name = movie_info.findAll('h1')[0].string
    movie_year = 'Release Year: ' + movie_info.findAll('h2')[0].string
    movie_genre = 'Genre: ' + movie_info.findAll('h2')[1].string.replace('/', ',')
    movie_rating = 'Rating: ' + movie_info.findAll('span', itemprop="ratingValue")[0].string
    # return xbmc.executebuiltin(ActivateWindow(movieinformation))
    return xbmcgui.Dialog().ok(movie_name, movie_year, movie_genre, movie_rating)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    xbmcgui.Dialog().ok('**Name', 'clicked')
    # # Create a playable item with a path to play.
    # play_item = xbmcgui.ListItem(path=path)
    # # Pass the item to the Kodi player.
    # xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

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
            list_videos(params['category'])
        elif params['action'] == 'show':
            # Play a video from a provided URL.
            # list_details(params['video'])
            # xbmc.log('log')
            xbmc.executebuiltin('ActivateWindow(movieinformation)')

        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
    # list_categories()
