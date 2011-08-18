import re
import urllib
import xml.dom.minidom
from urlparse import urlparse
import cgi

import twitter
import feedparser

def make_link(description, url, title = None):
    if title is not None and title != "":
        return '<a href="%s" title="%s">%s</a>' % (url, cgi.escape(title, True), cgi.escape(description, True))
    else:
        return '<a href="%s">%s</a>' % (url, cgi.escape(description, True))

def make_ul(items):
    return "<ul>\n" + "".join(["<li>%s</li>\n" % item for item in items]) + "</ul>"

def get_last_fm(user, api_key):
    params = urllib.urlencode({'method': 'user.getrecenttracks',
        'user': user, 'api_key': api_key})
    f = urllib.urlopen("http://ws.audioscrobbler.com/2.0/?%s" % params)
    # f = open("ws.audioscrobbler.com.xml", "r")
    xml_string = f.read()
    doc = xml.dom.minidom.parseString(xml_string)
    if doc.firstChild.nodeName == 'lfm' and \
            doc.firstChild.getAttribute('status') == 'ok':
        tracks = doc.getElementsByTagName('track')
        links = []
        for track in tracks:
            artist = track.getElementsByTagName('artist')[0].firstChild.nodeValue
            name = track.getElementsByTagName('name')[0].firstChild.nodeValue
            url = track.getElementsByTagName('url')[0].firstChild.nodeValue
            links.append(artist + " - " + make_link(name, url))
        return make_ul(links)

def get_delicious(user, password):
    f = urllib.urlopen("https://%s:%s@api.del.icio.us/v1/posts/recent" % (user, password))
    # f = open("delicious_recent.xml", "r")
    xml_string = f.read()
    doc = xml.dom.minidom.parseString(xml_string)
    posts = doc.getElementsByTagName("post")
    items = [make_delicious_html(post) for post in posts if is_public(post)]
    if len(items) > 0:
        result = make_ul(items[:5])
    else:
        result = "No recent entries"
    return result

def make_delicious_html(post):
    url = post.getAttribute("href")
    title = post.getAttribute("description")
    notes = post.getAttribute("extended")
    return make_link(title, url, notes) + " <span style=\"color: #808080;\">(" + get_domain(url) + ")</span>"

def get_twitter(user):
    api = twitter.Api()
    timeline = api.GetUserTimeline(user)
    items = []
    for status in timeline[:3]:
        items.append(format_tweet(status.text) + "<br/>" + make_link(status.relative_created_at, "http://twitter.com/%s/status/%s" % (user, status.id)))
    return make_ul(items)

def get_goodreads(id, shelf):
    f = feedparser.parse("http://www.goodreads.com/review/list_rss/%s?shelf=%s" % (id, shelf))
    items = []
    for entry in f.entries:
        items.append(make_link(entry.title, "http://www.goodreads.com/book/show/%s" % (entry.book_id)) + " by " + entry.author_name)
    return make_ul(items)

def get_so_answers(user_id):
    f = feedparser.parse("http://stackoverflow.com/feeds/user/%s" % user_id)
    answers = [entry for entry in f.entries if is_answer(entry)]
    answers.sort(key = lambda e : e.published_parsed, reverse = True)
    if len(answers) > 0:
        items = []
        for answer in answers[:5]:
            items.append(make_link(get_question_title(answer), get_question_link(answer)))
        return make_ul(items)
    else:
        return "No recent answers"

def is_answer(e):
    return e.title.startswith('Answer by ')

def is_public(post):
    return post.getAttribute("shared") != "no"

def get_question_title(entry):
    m = re.match("^Answer by mikej for (.+)$", entry.title)
    if m:
        return m.group(1)
    else:
        raise Exception("Entry %s is not an answer to a question" % entry.title)

def get_question_link(entry):
    link = entry.link
    prefix = "http://stackoverflow.com,"
    return link[len(prefix):] if link.startswith(prefix) else link

def format_tweet(tweet):
    tweet = re.sub("(http://[^\s]+)", "<a href=\"\\1\">\\1</a>", tweet)
    tweet = re.sub("@([a-zA-Z0-9_]+)", "@<a href=\"http://twitter.com/\\1\">\\1</a>", tweet)
    tweet = re.sub("#([a-zA-Z0-9_]+)", "<a href=\"http://twitter.com/search?q=\\1\">#\\1</a>", tweet)
    return tweet

def get_domain(url):
    hostname = urlparse(url)[1]
    if hostname.startswith("www."):
        return hostname[4:]
    else:
        return hostname
