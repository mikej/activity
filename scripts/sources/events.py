import urllib
import json
from dateutil.parser import parse as parse_date
from datetime import datetime

from utils import make_link, make_ul, make_date_range

def get_json_events(url):
    f = urllib.urlopen(url)
    raw_json = f.read()
    f.close()

    events_json = json.loads(raw_json)

    events = events_json.get('events', [])
    events = [event for event in events if upcoming(event)]
    items = []
    if len(events) > 0:
        events.sort(key = lambda e: parse_date(e.get('date')))
        for event in events:
            title = event.get('title', 'Untitled event')
            start_date = parse_date(event.get('date'))
            event_date_str = make_date_range(start_date, start_date) # only handle single day events for now
            event_tags = event.get('tags', [])
            event_url = event.get('url', None)
            entry = make_link(title, event_url) + "<br>"
            entry += event_date_str
            if len(event_tags) > 0:
                entry += "<br>"
                entry += " ".join([make_tag(tag) for tag in event_tags])
            items.append(entry)
        return make_ul(items)
    else:
        return "<p>No upcoming events</p>"

def upcoming(event):
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    event_date = parse_date(event.get('date'))
    return event_date >= today

def make_tag(tag):
    tag_class = tag.lower() # TODO convert spaces to "-" and strip non-alpha
    return "<span class=\"event-tag event-tag-" + tag_class + "\">" + tag + "</span>"
