import urllib
import json
from dateutil.parser import parse as parse_date
from datetime import datetime

from utils import make_link, make_ul

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
            title = event.get('title', 'Untiteld event')
            event_date = event.get('date')
            event_url = event.get('url', None)
            items.append(make_link(title, event_url) + "<br/>" + event_date)
        return make_ul(items)
    else:
        return "<p>No upcoming events</p>"

def upcoming(event):
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    event_date = parse_date(event.get('date'))
    return event_date >= today