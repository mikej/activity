from itertools import imap, groupby
from operator import itemgetter
import cgi
from urlparse import urlparse

# from http://stackoverflow.com/a/3463410/63034
def strip_consecutive_duplicates(iterable, key=None):
    return imap(next, imap(itemgetter(1), groupby(iterable, key)))

def make_link(description, url, title = None):
    if url is None:
        return description
    if title is not None and title != "":
        return '<a href="%s" title="%s">%s</a>' % (url, cgi.escape(title, True), cgi.escape(description, True))
    else:
        return '<a href="%s">%s</a>' % (url, cgi.escape(description, True))

def make_ul(items):
    return "<ul class=\"activity-items\">\n" + "".join(["<li>%s</li>\n" % item for item in items]) + "</ul>"

def get_domain(url):
    hostname = urlparse(url)[1]
    if hostname.startswith("www."):
        return hostname[4:]
    else:
        return hostname

def ordinal(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix

def make_date_range(start_date, end_date):
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
        return " ".join([start_day_of_month, start_month, start_year, "-", end_day_of_month, end_month, end_year])
    elif start_month != end_month:
        # if in the same year but different months display like "Friday, 30th November - Saturday, 1st December 2012"
        return " ".join([start_day_of_month, start_month, end_day_of_month, end_month,  end_year])
    else:
        # if in the same year and month display like "Saturday, 24th - Sunday 25th November 2012"
        return " ".join([start_day_of_month, "-", end_day_of_month, end_month, end_year])