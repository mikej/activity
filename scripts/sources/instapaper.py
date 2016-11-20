import feedparser
from utils import make_link, make_ul, get_domain

def get_instapaper_likes(feed_url):
    f = feedparser.parse(feed_url)
    entries = f.entries
    entries.sort(key = lambda e : e.updated_parsed, reverse = True)
    if len(entries) > 0:
        items = []
        for entry in entries[:5]:
            items.append(make_instapaper_favourite_html(entry))
        return make_ul(items)
    else:
        return "<p>No recent likes</p>"

def make_instapaper_favourite_html(entry):
    return make_link(entry.title, entry.link) + \
        " <span style=\"color: #808080;\">(" + get_domain(entry.link) + ")</span>"