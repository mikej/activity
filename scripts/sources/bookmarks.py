import urllib
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from urlparse import urlparse
from utils import make_link, make_ul, get_domain

def get_bookmarks(end_point, user = None, password = None, auth_token = None):
    if auth_token:
        url = end_point + "posts/recent?auth_token=" + auth_token + "&count=%d"
    else:
        url = ((end_point + "posts/recent") % (user, password)) + "?count=%d"
    # request with increasing count until list includes at least 5 public, read bookmarks
    for recent_count in (10, 25, 50, 75, 100):
        request_url = url % (recent_count)
        f = urllib.urlopen(request_url)
        xml_string = f.read()
        try:
            doc = xml.dom.minidom.parseString(xml_string)
        except ExpatError:
            raise Exception('An error occured parsing the recent bookmark response:\n%s' % xml_string)
        posts = doc.getElementsByTagName("post")
        items = [make_bookmark_html(post) for post in posts if is_public(post) and not is_unread(post)]
        if len(items) >= 5:
            break
    if len(items) > 0:
        result = make_ul(items[:5])
    else:
        result = "<p>No recent entries</p>"
    return result

def is_public(post):
    return post.getAttribute("shared") != "no"

def is_unread(post):
    return post.getAttribute("toread") == "yes"

def get_pinboard(auth_token):
    return get_bookmarks("https://api.pinboard.in/v1/", auth_token = auth_token)

def make_bookmark_html(post):
    url = post.getAttribute("href")
    title = post.getAttribute("description")
    notes = post.getAttribute("extended")
    return make_link(title, url, notes) + " <span style=\"color: #808080;\">(" + get_domain(url) + ")</span>"