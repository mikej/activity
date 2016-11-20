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