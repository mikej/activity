import re
import urllib
import xml.dom.minidom
from urlparse import urlparse
import cgi
from datetime import date, datetime, timedelta
from xml.parsers.expat import ExpatError

import pytz
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
    else:
        raise Exception('Unexpected response from last.fm: %s' % xml_string)

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

def get_pinboard(auth_token):
    return get_bookmarks("https://api.pinboard.in/v1/", auth_token = auth_token)

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
        return "<p>No recent answers</p>"

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
        return "<p>No recent activity</p>"

def get_events(username):
    f = urllib.urlopen("http://lanyrd.com/profile/%s/%s.attending.ics" % (username, username))
    cal = Calendar.from_ical(f.read())
    f.close()

    events = [component for component in cal.walk() if component.name == 'VEVENT' and not finished(component)]
    return events

def get_lanyrd(username):
    events = get_events(username)
    events.sort(key = lambda e: get_start_datetime(e))

    if len(events) > 0:
        items = []
        for event in events:
            event_title = event.get('SUMMARY')
            event_date = make_event_date(event)
            event_url = event.get('URL')
            items.append(make_link(event_title, event_url) + "<br/>" + event_date)
        return make_ul(items)
    else:
        return "<p>No upcoming events</p>"

def get_instapaper_likes(feed_url):
    f = feedparser.parse(feed_url)
    entries = f.entries
    entries.sort(key = lambda e : e.updated_parsed, reverse = True)
    if len(entries) > 0:
        items = []
        for entry in entries[:5]:
            items.append(make_link(entry.title, entry.link))
        return make_ul(items)
    else:
        return "<p>No recent likes</p>"

def make_bookmark_html(post):
    url = post.getAttribute("href")
    title = post.getAttribute("description")
    notes = post.getAttribute("extended")
    return make_link(title, url, notes) + " <span style=\"color: #808080;\">(" + get_domain(url) + ")</span>"

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

def is_unread(post):
    return post.getAttribute("toread") == "yes"

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

def get_domain(url):
    hostname = urlparse(url)[1]
    if hostname.startswith("www."):
        return hostname[4:]
    else:
        return hostname

def get_start_datetime(event):
    """If an event only specifies a start day but not a start time then the
    DTSTART will be a date object rather than a datetime object. This method
    ensures we have a datetime so that the start times of all events are
    comparable by sort."""
    dt = event.get('DTSTART').dt
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, date):
        # treat start time of the event as midnight UTC
        return pytz.utc.localize(datetime(dt.year, dt.month, dt.day))
    else:
        raise Exception("Unsupported start date type") 

def finished(event):
    event_end = get_end_datetime(event)
    now = datetime.now(pytz.utc)
    return now > event_end

def get_end_datetime(event):
    dt = event.get('DTEND').dt
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, date):
        # end dates seem to be 1 day too high for events that don't specify times
        # in the ical so subtract 1
        end_date = (dt - timedelta(days = 1))
        # only got the day but not the end time so assume ends at 23:59:59
        return pytz.utc.localize(datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59))
    else:
        raise Exception("Unsupported end date type") 

def make_event_date(event):
    start_datetime = get_start_datetime(event)
    start_date = date(start_datetime.year, start_datetime.month, start_datetime.day)
    end_datetime = get_end_datetime(event).get('DTEND').dt
    end_date = date(end_datetime.year, end_datetime.month, end_datetime.day)

    start_year = start_date.strftime('%Y')
    start_month = start_date.strftime('%-B')
    start_day_of_month = start_date.strftime('%A, ') + ordinal(start_date.day)
    
    end_year = end_date.strftime('%Y')
    end_month = end_date.strftime('%-B')
    end_day_of_month = end_date.strftime('%A, ') + ordinal(end_date.day)

    if start_date == end_date:
        # if same day then display like "Saturday, 8th December 2012"
        return " ".join([start_day_of_month, start_month, start_year])
    elif start_year != end_year:
        # if different years then display like "Monday, 31st December 2012 - Tuesday 1st January 2013"
        return " ".join([start_day_of_month, start_month, start_year, " - ", end_day_of_month, end_month, end_year])
    elif start_month != end_month:
        # if in the same year but different months display like "Friday, 30th November - Saturday, 1st December 2012"
        return " ".join([start_day_of_month, start_month, end_day_of_month, end_month,  end_year])
    else:
        # if in the same year and month display like "Saturday, 24th - Sunday 25th November 2012"
        return " ".join([start_day_of_month, " - ", end_day_of_month, end_month, end_year])

def ordinal(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix
