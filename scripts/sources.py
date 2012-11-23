import re
import urllib
import xml.dom.minidom
from urlparse import urlparse
import cgi
from datetime import date, datetime, timedelta
import pytz

import twitter # http://code.google.com/p/python-twitter/
import feedparser # http://feedparser.org/
from icalendar import Calendar

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
        items = []
        for track in tracks:
            artist = track.getElementsByTagName('artist')[0].firstChild.nodeValue
            name = track.getElementsByTagName('name')[0].firstChild.nodeValue
            url = track.getElementsByTagName('url')[0].firstChild.nodeValue
            items.append(artist + " - " + make_link(name, url))
        return make_ul(items)

def get_bookmarks(user, password, end_point):
    url = (end_point + "posts/recent") % (user, password)
    f = urllib.urlopen(url)
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

def get_delicious(user, password):
    return get_bookmarks(user, password, "https://%s:%s@api.del.icio.us/v1/")

def get_pinboard(user, password):
    return get_bookmarks(user, password, "https://%s:%s@api.pinboard.in/v1/")

def make_delicious_html(post):
    url = post.getAttribute("href")
    title = post.getAttribute("description")
    notes = post.getAttribute("extended")
    return make_link(title, url, notes) + " <span style=\"color: #808080;\">(" + get_domain(url) + ")</span>"

def get_twitter(user):
    api = twitter.Api()
    # try getting an increasing number of tweets until the timeline contains
    # at least 3 tweets that are not @replies
    for tweet_count in (20, 50, 100, 250):
        timeline = api.GetUserTimeline(user, count = tweet_count)
        items = []
        for status in timeline:
            if not is_at_reply(status):
                items.append(format_tweet(status.text) + "<br/>" + 
                    make_link(status.relative_created_at, "http://twitter.com/%s/status/%s" % (user, status.id)))
            if len(items) == 3: return make_ul(items)
    # didn't find 3 recent tweets, if *any* were found then return them
    # otherwise return a "No recent tweets messsage"
    if len(items) > 0:
        return make_ul(items)
    else:
        return "No recent tweets"

def is_at_reply(status):
    return status.text.startswith('@')

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

def get_github_activity(user):
    f = feedparser.parse("http://github.com/%s.atom" % user)
    entries = f.entries
    entries.sort(key = lambda e : e.published_parsed, reverse = True)
    if len(entries) > 0:
        items = []
        for entry in entries[:5]:
            title = re.sub("^%s " % user, "", entry.title).capitalize()
            items.append(make_link(title, entry.link))
        return make_ul(items)
    else:
        return "No recent activity"        

def make_link(description, url, title = None):
    if title is not None and title != "":
        return '<a href="%s" title="%s">%s</a>' % (url, cgi.escape(title, True), cgi.escape(description, True))
    else:
        return '<a href="%s">%s</a>' % (url, cgi.escape(description, True))

def make_ul(items):
    return "<ul>\n" + "".join(["<li>%s</li>\n" % item for item in items]) + "</ul>"

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

def get_lanyrd(username):
    f = urllib.urlopen("http://lanyrd.com/profile/%s/%s.attending.ics" % (username, username))
    cal = Calendar.from_ical(f.read())
    f.close()

    events = [component for component in cal.walk() if component.name == 'VEVENT']
    events.sort(key = lambda e: get_datetime(e))

    items = []
    for event in events:
        event_title = event.get('SUMMARY')
        event_date = make_event_date(event)
        event_url = event.get('URL')
        items.append(make_link(event_title, event_url) + "<br/>" + event_date)
    return make_ul(items)

def get_datetime(event):
    """If an event only specifies a start day but not a start time then the
    DTSTART will be a date object rather than a datetime object. This method
    ensures we have a datetime so that the start times of all events are
    comparable by sort."""
    dt = event.get('DTSTART').dt
    if isinstance(dt, datetime):
        return dt
    else:
        # treat start time of the event as midnight UTC
        return pytz.utc.localize(datetime(dt.year, dt.month, dt.day))

def make_event_date(event):
    start_date = event.get('DTSTART').dt
    start_year = start_date.strftime('%Y')
    start_month = start_date.strftime('%-B')
    start_day_of_month = start_date.strftime('%A, ') + ordinal(start_date.day)
    # end dates seem to be 1 day too many in the ical so subtract 1
    end_date = (event.get('DTEND').dt - timedelta(days = 1))
    end_year = end_date.strftime('%Y')
    end_month = end_date.strftime('%-B')
    end_day_of_month = end_date.strftime('%A, ') + ordinal(end_date.day)

    if start_date == end_date:
        return " ".join([start_day_of_month, start_month, start_year])
    elif start_year != end_year:
        return " ".join([start_day_of_month, start_month, start_year, " - ", end_day_of_month, end_month, end_year])
    elif start_month != end_month:
        return " ".join([start_day_of_month, start_month, end_day_of_month, end_month,  end_year])
    else:
        return " ".join([start_day_of_month, " - ", end_day_of_month, end_month, end_year])

def ordinal(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix