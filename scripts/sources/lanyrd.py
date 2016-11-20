import urllib
from icalendar import Calendar
from utils import make_link, make_ul, make_date_range
import pytz
from datetime import date, datetime, timedelta

def get_events(username):
    f = urllib.urlopen("http://lanyrd.com/profile/%s/%s.attending.ics" % (username, username))
    content = f.read()
    status = f.getcode()
    f.close()
    if status == 200:
        cal = Calendar.from_ical(content)

        events = [component for component in cal.walk() if component.name == 'VEVENT' and not finished(component)]
        return events
    else:
        raise Exception("Lanyrd returned status %d: %s" % (status, content))

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
    end_datetime = get_end_datetime(event)
    end_date = date(end_datetime.year, end_datetime.month, end_datetime.day)
    return make_date_range(start_date, end_date)
