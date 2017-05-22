import urllib
import xml.dom.minidom
from utils import strip_consecutive_duplicates, make_ul, make_link
from itertools import islice

def get_last_fm(user, api_key):
    params = urllib.urlencode({'method': 'user.getrecenttracks',
        'user': user, 'api_key': api_key, 'limit': 200})
    f = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?%s" % params)
    # f = open("ws.audioscrobbler.com.xml", "r")
    xml_string = f.read()
    doc = xml.dom.minidom.parseString(xml_string)
    if doc.firstChild.nodeName == 'lfm' and \
            doc.firstChild.getAttribute('status') == 'ok':
        tracks = doc.getElementsByTagName('track')
        return make_ul(islice(strip_consecutive_duplicates([last_fm_track_link(track) for track in tracks]), 10))
    else:
        raise Exception('Unexpected response from last.fm: %s' % xml_string)

def last_fm_track_link(track):
    artist = track.getElementsByTagName('artist')[0].firstChild.nodeValue
    name = track.getElementsByTagName('name')[0].firstChild.nodeValue
    url = track.getElementsByTagName('url')[0].firstChild.nodeValue
    return make_link(name, url) + " - " + artist
